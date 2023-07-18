from flask import Flask, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, current_user
import jwt
from datetime import datetime, timedelta
from models import User, Recipe, SharedVocToRecipe, SharedVoc, RecipeToUser
from db import db
import requests
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:recipe_manager@pg_container:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db.init_app(app)

def user_token_check(headers):
    r = requests.get('http://auth-service:8000/token-check', headers=headers)
    return r.status_code == 200, r.json()

@app.route('/favourites', methods=['GET'])
def get_favourites():
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    
    email = user_json['user']['email']
    user = User.query.filter_by(email=email).first()

    favourites = RecipeToUser.query.filter_by(users_id=user.id).all()
    if not favourites or len(favourites) == 0:
        return jsonify({'message': 'No favourites found'}), 404
    
    return jsonify([fav.recipes_id for fav in favourites]), 200

@app.route('/favourites/<int:recipe_id>', methods=['POST'])
def add_favourite(recipe_id):
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    
    email = user_json['user']['email']
    user = User.query.filter_by(email=email).first()

    recipe = Recipe.query.filter_by(id=recipe_id).first()
    if not recipe:
        return jsonify({'message': 'Recipe not found'}), 404

    favourite = RecipeToUser.query.filter_by(users_id=user.id, recipes_id=recipe_id).first()
    if favourite:
        return jsonify({'message': 'Recipe already in favourites'}), 400

    new_favourite = RecipeToUser(users_id=user.id, recipes_id=recipe_id)
    db.session.add(new_favourite)
    db.session.commit()

    return jsonify({'message': 'Recipe added to favourites'}), 200

@app.route('/favourites/<int:recipe_id>', methods=['DELETE'])
def delete_favourite(recipe_id):
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    
    email = user_json['user']['email']
    user = User.query.filter_by(email=email).first()

    recipe = Recipe.query.filter_by(id=recipe_id).first()
    if not recipe:
        return jsonify({'message': 'Recipe not found'}), 404

    favourite = RecipeToUser.query.filter_by(users_id=user.id, recipes_id=recipe_id).first()
    if not favourite:
        return jsonify({'message': 'Recipe not in favourites'}), 400

    db.session.delete(favourite)
    db.session.commit()

    return jsonify({'message': 'Recipe removed from favourites'}), 200

@app.route('/favourites/check/<int:recipe_id>', methods=['GET'])
def check_favourite(recipe_id):
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    
    email = user_json['user']['email']
    user = User.query.filter_by(email=email).first()

    recipe = Recipe.query.filter_by(id=recipe_id).first()
    if not recipe:
        return jsonify({'message': 'Recipe not found'}), 404

    favourite = RecipeToUser.query.filter_by(users_id=user.id, recipes_id=recipe_id).first()
    if not favourite:
        return jsonify({'message': 'Recipe not in favourites'}), 404

    return jsonify({'message': 'Recipe in favourites'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8004, debug=True)