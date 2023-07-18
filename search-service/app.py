from flask import Flask, jsonify, request
from models import User, Recipe, SharedVoc, SharedVocToRecipe
from db import db
import requests
from sqlalchemy import DDL, or_, and_
from sqlalchemy.sql import func
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

def get_ingredients(id):
    connections = SharedVocToRecipe.query.filter_by(recipes_id=id).all()
    ingredients = []
    for connection in connections:
        ingredients.append(SharedVoc.query.filter_by(id=connection.shared_voc_id).first())
    return ingredients

@app.route('/search/recipes', methods=['POST'])
def search_recipes():
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    data = request.get_json()
    term = data.get('term')
    shared_voc_ids = data.get('shared_voc_ids')
    
    # results = Recipe.query.filter(
    #     Recipe.title.ilike(f'%{term}%')
    # ).filter_by().all()
    if shared_voc_ids is None or len(shared_voc_ids) == 0:
        app.logger.info("First if")
        app.logger.info("term: %s", term)
        app.logger.info("shared_voc_ids: %s", shared_voc_ids)
        results = Recipe.query.filter(
            Recipe.title.ilike(f'%{term}%')
        ).all()
        return jsonify([rec.json(get_ingredients(rec.id)) for rec in results]), 200
    elif term is None or len(term) == 0 or term == '':
        app.logger.info("Second if")
        app.logger.info("term: %s", term)
        app.logger.info("shared_voc_ids: %s", shared_voc_ids)
        results = db.session.query(SharedVocToRecipe, Recipe, SharedVoc).filter(
            Recipe.id == SharedVocToRecipe.recipes_id).filter(
            SharedVocToRecipe.shared_voc_id == SharedVoc.id).filter(
            SharedVoc.id.in_(shared_voc_ids)).distinct(Recipe.id)
        
        return jsonify([rec.Recipe.json(get_ingredients(rec.Recipe.id)) for rec in results]), 200
    else:
        app.logger.info("else")
        app.logger.info("term: %s", term)
        app.logger.info("shared_voc_ids: %s", shared_voc_ids)
        results = db.session.query(SharedVocToRecipe, Recipe, SharedVoc).filter(
            Recipe.id == SharedVocToRecipe.recipes_id).filter(
            SharedVocToRecipe.shared_voc_id == SharedVoc.id).filter(
            or_(Recipe.title.ilike(f'%{term}%'), SharedVoc.id.in_(shared_voc_ids))).distinct(Recipe.id)
        
        return jsonify([rec.Recipe.json(get_ingredients(rec.Recipe.id)) for rec in results]), 200

@app.route('/search/shared_voc', methods=['POST'])
def search_shared_voc():
    accepted, user_json = user_token_check(request.headers)
    if not accepted:
        return jsonify({'message': 'Invalid token'}), 401
    data = request.get_json()
    term = data.get('term')
    type = data.get('type')
    
    results = SharedVoc.query.filter(
        and_(SharedVoc.name.ilike(f'%{term}%'), SharedVoc.type == type)
    ).all()

    return jsonify([sv.json() for sv in results]), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8005, debug=True)