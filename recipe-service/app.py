from flask import Flask, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, current_user
import jwt
from datetime import datetime, timedelta
from models import User, Recipe, SharedVocToRecipe, SharedVoc
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
    app.logger.info("Token check response: %s", r.status_code)
    app.logger.info("Token check response: %s", r.content)
    return r.status_code == 200, r.json()

def get_ingredients(id):
    connections = SharedVocToRecipe.query.filter_by(recipes_id=id).all()
    ingredients = []
    for connection in connections:
        ingredients.append(SharedVoc.query.filter_by(id=connection.shared_voc_id).first())
    return ingredients

@app.route('/recipes', methods=['GET'])
def get_recipes():
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    recipes_with_ingredients = []
    recipes = Recipe.query.all()
    app.logger.info("Found %s recipes", len(recipes))
    for recipe in recipes:
        recipes_with_ingredients.append(recipe.json(get_ingredients(recipe.id)))

    return jsonify(recipes_with_ingredients), 200
    

@app.route('/recipes/by_recipe_id/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    recipe = Recipe.query.filter_by(id=recipe_id).first()
    if not recipe:
        return jsonify({'message': 'Recipe not found'}), 404
    ingredients = get_ingredients(recipe_id)
    return jsonify(recipe.json(ingredients)), 200


@app.route('/recipes/by_user_id/<int:user_id>', methods=['GET'])
def get_user_recipes(user_id):
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    
    recipes = Recipe.query.filter_by(user_id=user_id).all()
    if not recipes or len(recipes) == 0:
        return jsonify({'message': 'No recipes found'}), 404
    
    recipes_with_ingredients = []
    for recipe in recipes:
        recipes_with_ingredients.append(recipe.json(get_ingredients(recipe.id)))
    
    return jsonify(recipes_with_ingredients), 200


@app.route('/recipes', methods=['POST'])
def create_recipe():
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    
    id = user_json["user"]['id']
    user = User.query.filter_by(id=id).first()

    data = request.get_json()

    title = data.get('title')
    description = data.get('description')
    ingredients = data.get('ingredients')
    instructions = data.get('instructions')
    cooking_time = data.get('cooking_time')
    serving_size = data.get('serving_size')
    

    if not id or not title or not description or not ingredients or not instructions:
        return jsonify({'message': 'Missing required fields'}), 400
    
    recipe = Recipe(
        title=title,
        description=description,
        instructions=instructions,
        user_id=user.id,
        cooking_time=cooking_time,
        serving_size=serving_size
    )

    db.session.add(recipe)
    db.session.flush()

    db.session.refresh(recipe)

    for ingredient in ingredients:
        db.session.add(SharedVocToRecipe(ingredient, recipe.id))

    db.session.commit()

    return jsonify({'message': 'Recipe created'}), 201

@app.route('/recipes/<int:id>', methods=['PUT'])
def update_recipe(id):
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    
    email = str(user_json['user']['email'])
    user = User.query.filter_by(email=email).first()

    data = request.get_json()

    title = data.get('title')
    description = data.get('description')
    ingredients = data.get('ingredients')
    instructions = data.get('instructions')
    cooking_time = data.get('cooking_time')
    serving_size = data.get('serving_size')

    recipe = Recipe.query.filter_by(id=id, user_id=user.id).first()

    if not recipe:
        return jsonify({'message': 'Recipe not found'}), 404
    
    if ingredients:
        connections = SharedVocToRecipe.query.filter_by(recipes_id=id).all()
        for connection in connections:
            db.session.delete(connection)
        for ingredient in ingredients:
            db.session.add(SharedVocToRecipe(ingredient, recipe.id))

    if title:
        recipe.name = title
    if description:
        recipe.description = description
    if instructions:
        recipe.instructions = instructions
    if cooking_time:
        recipe.cooking_time = cooking_time
    if serving_size:
        recipe.serving_size = serving_size

    db.session.commit()

    return jsonify({'message': 'Recipe updated'}), 200

@app.route('/recipes/<int:id>', methods=['DELETE'])
def delete_recipe(id):
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    recipe = Recipe.query.filter_by(id=id).first()
    if not recipe:
        return jsonify({'message': 'Recipe not found'}), 404
    
    connections = SharedVocToRecipe.query.filter_by(recipes_id=id).all()
    for connection in connections:
        db.session.delete(connection)
        db.session.flush()
    
    db.session.delete(recipe)
    db.session.commit()

    return jsonify({'message': 'Recipe deleted'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)