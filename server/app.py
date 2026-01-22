from flask import Flask, jsonify
from flask_migrate import Migrate


from config import Config
from models import db, bcrypt

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)


    db.init_app(app)
    bcrypt.init_app(app)
    Migrate(app,db)

    @app.get("/")
    def home():
        return jsonify({"status": "ok"}), 200
    
    return app

app = create_app()

if __name__== "__main__":
    app.run(port=5555, debug=True)