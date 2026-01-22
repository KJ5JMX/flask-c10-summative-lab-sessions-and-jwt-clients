from flask import Flask, jsonify
from flask_migrate import Migrate
from flask import request 
from flask_jwt_extended import   (
    
    create_access_token,
    jwt_required,
    get_jwt_identity,

)

from sqlalchemy.exc import IntegrityError
from models import User, Note
from flask_jwt_extended import JWTManager


jwt = JWTManager()


from config import Config
from models import db, bcrypt

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)


    db.init_app(app)
    bcrypt.init_app(app)
    Migrate(app,db)
    jwt.init_app(app)

    @app.get("/")
    def home():
        return jsonify({"status": "ok"}), 200
    
    
    @app.get("/me")
    @jwt_required()
    def me():
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "user not found"}), 404
        
        return jsonify(user.to_dict()), 200
    
    #signup
    @app.post("/signup")
    def signup():
        data = request.get_json() or {}
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""

        if not username or not password:
            return jsonify({"error": "username and password are required"}), 400
        
        user = User(username=username)

        try:
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "username already taken"}), 400
        except ValueError as ev:
            db.session.rollback()
            return jsonify({"error": str(ev)}), 400
        
        return jsonify(user.to_dict()), 201
    

    #login
    @app.post("/login")
    def login():
        data = request.get_json() or {}
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return jsonify({"error": "invalid username or password"}), 401
        
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200
    

    #notes
    @app.get("/notes")
    @jwt_required()
    def get_notes():
        user_id = get_jwt_identity()

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        pagination = (
            Note.query
            .filter_by(user_id=user_id)
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        notes = [note.to_dict() for note in pagination.items]
        return jsonify({
            "notes": notes, 
            "page": page, 
            "per_page": per_page,
            "total": pagination.total,
        }), 200
    

    #notes create
    @app.post("/notes")
    @jwt_required()
    def create_note():
        user_id = get_jwt_identity()
        data = request.get_json() or {}

        title = (data.get("title") or "").strip()
        content = (data.get("content") or "").strip()

        if not title:
            return jsonify({"error": "title is required"}), 400
        if not content:
            return jsonify({"error": "content is required"}), 400
        
        try:
            note = Note(user_id=user_id, title=title, content=content)
            db.session.add(note)
            db.session.commit()
        except ValueError as ve:
            db.session.rollback()
            return jsonify({"error": str(ve)}), 400
        
        return jsonify(note.to_dict()), 201
    


    @app.get("/notes/<int:note_id>")
    @jwt_required()
    def get_note(note_id):
        user_id = get_jwt_identity()

        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        if not note:
            return jsonify({"error": "note not found"}), 404

        return jsonify(note.to_dict()), 200


    @app.patch("/notes/<int:note_id>")
    @jwt_required()
    def update_note(note_id):
        user_id = get_jwt_identity()
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()

        if not note:
            return jsonify({"error": "note not found"}), 404

        data = request.get_json() or {}

        if "title" not in data and "content" not in data:
            return jsonify({"error": "title or content required to update"}), 400

        
        if "title" in data:
            note.title = (data.get("title") or "").strip()
        if "content" in data:
            note.content = (data.get("content") or "").strip()

        try:
            db.session.commit()
        except ValueError as ev:
            db.session.rollback()
            return jsonify({"error": str(ev)}), 400

        return jsonify(note.to_dict()), 200


    @app.delete("/notes/<int:note_id>")
    @jwt_required()
    def delete_note(note_id):
        user_id = get_jwt_identity()
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()

        if not note:
            return jsonify({"error": "note not found"}), 404

        db.session.delete(note)
        db.session.commit()
        return "", 204


    
    return app

app = create_app()

if __name__== "__main__":
    app.run(port=5555, debug=True)