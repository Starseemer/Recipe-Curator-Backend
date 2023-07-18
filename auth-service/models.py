from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash

from db import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    sha256_password = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    user_session_token = db.Column(db.String(256), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'surname': self.surname
        }

    def set_session_token(self, token):
        self.user_session_token = token
    
    def check_session_token(self, token):
        return self.user_session_token == token

    def set_password(self, password):
        self.sha256_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.sha256_password, password)