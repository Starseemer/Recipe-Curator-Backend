from flask import Flask, jsonify, request, redirect, url_for
import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, current_user
import jwt
from datetime import datetime, timedelta
from models import User, Recipe, SharedVoc, Comment
from db import db
import requests
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:recipe_manager@pg_container:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app) #Add cors to allow cross origin requests
db.init_app(app)

def user_token_check(headers):
    r = requests.get('http://auth-service:8000/token-check', headers=headers)
    return r.status_code == 200, r.json()

@app.route('/comments/<int:shared_voc_id>', methods=['GET'])
def get_comments(shared_voc_id):
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    comments = Comment.query.filter_by(shared_voc_id=shared_voc_id).all()

    if not comments or len(comments) == 0:
        return jsonify({'message': 'No comments found'}), 404
    return jsonify([comment.json() for comment in comments]), 200

@app.route('/comments/<int:shared_voc_id>', methods=['POST'])
def create_comment(shared_voc_id):
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    
    app.logger.info("Creating comment with user id: %s", user_json['user']['email'])
    
    email = str(user_json['user']['email'])
    user = User.query.filter_by(email=email).first()

    data = request.get_json()

    body = data.get('body')
    user_email = user.email

    if not body or not user_email:
        return jsonify({'message': 'Missing required fields'}), 400

    comment = Comment(body=body, shared_voc_id=shared_voc_id, user_email=user_email)
    db.session.add(comment)
    db.session.commit()

    return jsonify(comment.json()), 201

@app.route('/comments/<int:id>', methods=['PUT'])
def update_comment(id):
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    
    app.logger.info("Updating comment with user id: %s", user_json['user']['email'])
    
    email = str(user_json['user']['email'])
    user = User.query.filter_by(email=email).first()

    comment = Comment.query.filter_by(id=id, user_id=user.id).first()

    if not comment:
        return jsonify({'message': 'Comment not found'}), 404

    data = request.get_json()

    body = data.get('body')

    if not body:
        return jsonify({'message': 'Missing required fields'}), 400
    
    comment.body = body
    
    db.session.commit()

    return jsonify(comment.json()), 200

@app.route('/comments/<int:id>', methods=['DELETE'])
def delete_comment(id):
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    
    email = str(user_json['user']['email'])
    user = User.query.filter_by(email=email).first()

    comment = Comment.query.filter_by(id=id, user_id=user.id).first()

    if not comment:
        return jsonify({'message': 'Comment not found'}), 404

    db.session.delete(comment)
    db.session.commit()

    return jsonify({'message': 'Comment deleted'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8003, debug=True)