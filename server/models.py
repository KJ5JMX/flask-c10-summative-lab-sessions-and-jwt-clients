from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from flask_bcrypt import Bcrypt

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})


db = SQLAlchemy(metadata=metadata)
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = "users" 

    id = db.Column(db.Integer, primary_key=True)


    
    username = db.Column(db.String, unique=True, nullable=False)

    #store hashed pass
    password_hash = db.Column(db.String, nullable=False)


    #releationship to owned source
    notes = db.relationship("Note", back_populates="user", cascade="all, delete-orphan")

    @validates("username")
    def validate_username(self, key, value):
        if not value or not value.strip():
            raise ValueError("usernameis required")
        return value.strip()
    
    def set_password(self, password):
        if not password or len(password) < 6:
            raise ValueError("password must be at least 6 characters long")
        hashed = bcrypt.generate_password_hash(password.encode('utf-8 '))
        self.password_hash = hashed.decode('utf-8') 

    def check_password(self, password: str) -> bool:
        if not password:
            return False
        return bcrypt.check_password_hash(self.password_hash, password.encode('utf-8'))
    
    #do not shot password hash
    def to_dict(self):
        return {"id": self.id, "username": self.username}
    




class Note(db.Model):
    __tablename__ = "notes" 

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="notes")


    @validates("title", "content")
    def validate_required_text(self, key, value):
        if not value or not str(value).strip():
            raise ValueError(f"{key} is required")
        return str(value).strip()
    
    def to_dict(self):
        return { 
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "user_id": self.user_id
        }



