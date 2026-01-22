from flask import Flask, jsonify
from flask_migrate import Migrate
from flask import request 
from flask_jwt_extended import   (
    
    create_access_token,
    jwt_required,
    get_jwt_identity,

)
import jwt
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


    
    return app

app = create_app()

if __name__== "__main__":
    app.run(port=5555, debug=True)