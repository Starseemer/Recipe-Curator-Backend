from flask import Flask, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, current_user
import jwt
from datetime import datetime, timedelta
from models import User
from db import db
#Add cors to allow cross origin requests
from flask_cors import CORS


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:recipe_manager@pg_container:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)

db.init_app(app)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    surname = data.get('surname')

    if not email or not password or not name or not surname:
        return jsonify({'message': 'Missing required fields'}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'message': 'Email already registered'}), 409

    user = User(
        
        email=email,
        name=name,
        surname=surname
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Registration successful'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing email or password'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid email or password'}), 401

    # Generate a JWT token
    token = jwt.encode(
        {'email': email, 'exp': datetime.utcnow() + timedelta(hours=48)},
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )

    # Set the user's session token
    user.set_session_token(token)
    db.session.commit()

    return jsonify({'token': token}), 200

@app.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    email = data.get('email')

    user = User.query.filter_by(email=email).first()

    token = data.get('token')

    if not user.check_session_token(token):
        return jsonify({'message': 'Not logged in'}), 401

    current_user.set_session_token(None)
    db.session.commit()

    return jsonify({'message': 'Logout successful'}), 200

@app.route('/token-check', methods=['GET'])
def token_check():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Missing token'}), 401

    user, code = get_user_from_token(token)
    #app.logger.info("Printing user " + str(user))
    if not user or code != 200:
        return jsonify({'message': 'Invalid token'}), 401

    return jsonify({'user': user.to_dict()}), 200

@app.route('/user', methods=['GET'])
def get_user():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Missing token'}), 401

    user, code = get_user_from_token(token)
    if not user or code != 200:
        return jsonify({'message': 'Invalid token'}), 401

    return jsonify({'user': user.to_dict()}), 200

@app.route('/user', methods=['PUT'])
def update_user():
    data = request.get_json()
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Missing token'}), 401

    user, code = get_user_from_token(token)
    if not user or code != 200:
        return jsonify({'message': 'Invalid token'}), 401

    user.name = data.get('name')
    user.surname = data.get('surname')
    if (user.check_password(data.get('oldPassword'))):
        user.set_password(data.get('newPassword'))

    db.session.commit()

    return jsonify({'user': user.to_dict()}), 200

def get_user_from_token(token):
    
    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        email = decoded_token['email']  # This is the email of the user that sent the request
        exp = decoded_token["exp"]
        app.logger.info("Printing email, exp " + str(email) + str(exp) + " " + str(datetime.utcnow()))
        if datetime.fromtimestamp(exp) < datetime.utcnow():
            # app.logger.info("Token expired")
            return jsonify({'message': 'Token expired'}), 401
        
        user = User.query.filter_by(email=email).first()
        # app.logger.info("Printing user" + str(type(user)))
        return user, 200
    except:
        # app.logger.info("Exception")
        return jsonify({'message': 'Unauthorized token!'}), 401

app.run(debug = True, host='0.0.0.0', port=8000)