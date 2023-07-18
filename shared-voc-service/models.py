from db import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text)
    instructions = db.Column(db.Text)
    cooking_time = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    serving_size = db.Column(db.Integer)

    def __init__(self, title, description=None, instructions=None, cooking_time=None,
                 user_id=None, serving_size=None):
        self.title = title
        self.description = description
        self.instructions = instructions
        self.cooking_time = cooking_time
        self.user_id = user_id
        self.serving_size = serving_size

class SharedVoc(db.Model):
    __tablename__ = 'shared_voc'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    desc = db.Column(db.Text)
    type = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, name, desc=None, type=None, user_id=None):
        self.name = name
        self.desc = desc
        self.type = type
        self.user_id = user_id

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            "desc": self.desc,
            "type": self.type,
            "user_id": self.user_id
        }

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.Text, db.ForeignKey('users.email'))
    body = db.Column(db.Text)
    shared_voc_id = db.Column(db.Integer, db.ForeignKey('shared_voc.id'), nullable=False)

    def __init__(self, user_email, body, shared_voc_id):
        self.user_email = user_email
        self.body = body
        self.shared_voc_id = shared_voc_id

    def json(self):
        return {
            'id': self.id,
            'comment': self.body,
            'shared_voc_id': self.shared_voc_id,
            'user_email': self.user_email
        }

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
    

class RecipeToUser(db.Model):
    __tablename__ = 'recipes_to_users'

    recipes_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), primary_key=True)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    def __init__(self, recipes_id, users_id):
        self.recipes_id = recipes_id
        self.users_id = users_id

class SharedVocToRecipe(db.Model):
    __tablename__ = 'shared_voc_to_recipes'

    shared_voc_id = db.Column(db.Integer, db.ForeignKey('shared_voc.id'), primary_key=True)
    recipes_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), primary_key=True)

    def __init__(self, shared_voc_id, recipes_id):
        self.shared_voc_id = shared_voc_id
        self.recipes_id = recipes_id