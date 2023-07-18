from flask import Flask, jsonify, request, redirect, url_for
import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, current_user
import jwt
from datetime import datetime, timedelta
from models import User, Recipe, SharedVoc
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

@app.route('/ingredients', methods=['GET'])
def get_ingredients():
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    ingredients = SharedVoc.query.filter_by(type="Ingredient").all()
    if not ingredients or len(ingredients) == 0:
        return jsonify({'message': 'No ingredients found'}), 404
    return jsonify([ing.json() for ing in ingredients]), 200

@app.route('/ingredients/<int:id>', methods=['GET'])
def get_ingredient(id):
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    ingredient = SharedVoc.query.filter_by(id=id, type="Ingredient").first()
    if not ingredient:
        return jsonify({'message': 'Ingredient not found'}), 404
    return jsonify(ingredient.json()), 200

@app.route('/ingredients', methods=['POST'])
def create_ingredient():
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    
    app.logger.info("Creating ingredient with user id: %s", user_json['user']['email'])
    
    email = str(user_json['user']['email'])
    user = User.query.filter_by(email=email).first()

    data = request.get_json()

    name = data.get('name')
    type = "Ingredient"
    description = data.get('desc')

    if not id or not name or not type:
        return jsonify({'message': 'Missing required fields'}), 400
    
    if not description:
        description = ""

    app.logger.info("Creating ingredient with id: %s, name: %s, type: %s, description: %s", id, name, type, description)
    shared_voc = SharedVoc(
        name=name,
        type=type,
        desc = description,
        user_id=user.id
    )

    db.session.add(shared_voc)
    db.session.commit()

    return jsonify({'message': 'Ingredient created'}), 201

@app.route('/ingredients/<int:id>', methods=['PUT'])
def update_ingredient(id):
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    data = request.get_json()

    email = str(user_json['user']['email'])
    user = User.query.filter_by(email=email).first()

    ingredient = SharedVoc.query.filter_by(id=id, user_id=user.id).first()

    if not ingredient:
        return jsonify({'message': 'Ingredient not found or Unauthorized'}), 404


    name = data.get('name')
    desc = data.get('desc')

    if name:
        ingredient.name = name
    if desc:
        ingredient.desc = desc

    db.session.commit()

    return jsonify({'message': 'Ingredient updated'}), 200

@app.route('/ingredients/<int:id>', methods=['DELETE'])
def delete_ingredient(id):
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    email = str(user_json['user']['email'])
    user = User.query.filter_by(email=email).first()

    ingredient = SharedVoc.query.filter_by(id=id, user_id=user.id).first()

    if not ingredient:
        return jsonify({'message': 'Ingredient not found or Unauthorized'}), 404

    db.session.delete(ingredient)
    db.session.commit()

    return jsonify({'message': 'Ingredient deleted'}), 200

@app.route('/cooking-terms', methods=['GET'])
def get_cooking_terms():
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    cts = SharedVoc.query.filter_by(type="CookingTerms").all()
    if not cts or len(cts) == 0:
        return jsonify({'message': 'No cooking terms found'}), 404
    return jsonify([ct.json() for ct in cts]), 200

@app.route('/cooking-terms/<int:id>', methods=['GET'])
def get_cooking_term(id):
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    ct = SharedVoc.query.filter_by(id=id, type="CookingTerms").first()
    if not ct:
        return jsonify({'message': 'Cooking term not found'}), 404
    return jsonify(ct.json()), 200

@app.route('/cooking-terms', methods=['POST'])
def create_cooking_term():
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    
    app.logger.info("Creating cooking term with user id: %s", user_json['user']['email'])
    
    email = str(user_json['user']['email'])
    user = User.query.filter_by(email=email).first()

    data = request.get_json()

    name = data.get('name')
    type = "CookingTerms"
    description = data.get('desc')

    if not id or not name or not type:
        return jsonify({'message': 'Missing required fields'}), 400
    
    if not description:
        description = ""

    app.logger.info("Creating cooking term with id: %s, name: %s, type: %s, description: %s", id, name, type, description)
    shared_voc = SharedVoc(
        name=name,
        type=type,
        desc = description,
        user_id=user.id
    )

    db.session.add(shared_voc)
    db.session.commit()

    return jsonify({'message': 'Cooking term created'}), 201

@app.route('/cooking-terms/<int:id>', methods=['PUT'])
def update_cooking_term(id):
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    data = request.get_json()

    email = str(user_json['user']['email'])
    user = User.query.filter_by(email=email).first()

    ct = SharedVoc.query.filter_by(id=id, user_id=user.id, type="CookingTerms").first()

    if not ct:
        return jsonify({'message': 'Cooking term not found or Unauthorized'}), 404


    name = data.get('name')
    type = data.get('type')
    desc = data.get('desc')

    if name:
        ct.name = name
    if type:
        ct.type = type
    if desc:
        ct.desc = desc

    db.session.commit()

    return jsonify({'message': 'Cooking term updated'}), 200

@app.route('/cooking-terms/<int:id>', methods=['DELETE'])
def delete_cooking_term(id):
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    email = str(user_json['user']['email'])
    user = User.query.filter_by(email=email).first()

    ct = SharedVoc.query.filter_by(id=id, user_id=user.id, type="CookingTerms").first()

    if not ct:
        return jsonify({'message': 'Cooking term not found or Unauthorized'}), 404

    db.session.delete(ct)
    db.session.commit()

    return jsonify({'message': 'Cooking term deleted'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002, debug=True)