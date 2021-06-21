import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# Initialize a database.
db_drop_and_create_all()

# ROUTES

@app.route("/drinks")
def get_drinks():
    '''
    Handles GET requests for drinks.
    '''

    try:
        drinks_query = Drink.query.all()
        drinks = [drink.short() for drink in drinks_query]

        return jsonify({
            "success": True,
            "drinks": drinks
        }), 200
    except Exception as e:
        abort(422)

@app.route("/drinks-detail")
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    '''
    Handles GET requests for drink details.
    '''

    try:
        drinks_query = Drink.query.all()
        drinks = [drink.long() for drink in drinks_query]

        return jsonify({
            "success": True,
            "drinks": drinks
        }), 200
    except Exception as e:
        abort(422)

@app.route("/drinks", methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    '''
    Handles POST requests to add a drink to the database.
    '''

    data = request.get_json()

    try:
        new_drink = Drink(
            title=data.get('title'),
            recipe=json.dumps(data.get('recipe'))
        )

        new_drink.insert()

        return jsonify({
            'success': True,
            'drinks': new_drink.long()
        }), 200
    except Exception:
        abort(422)

@app.route("/drinks/<int:drink_id>", methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    '''
    Handles PATCH requests to update drink details.
    '''

    data = request.get_json()
    drink = Drink.query.filter(Drink.id==drink_id).one_or_none()

    if not drink:
         return json.dumps({
                "success": False,
                "error": 'Drink #' + drink_id + ' not found to be edited'
            }), 404

    try:
        if data.get('title', None):
            drink.title = data.get('title')

        if data.get('recipe', None):
            drink.recipe = json.dumps(data.get('recipe'))

        drink.update()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    except Exception:
        abort(422)

@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    '''
    Handles DELETE requests to delete a drink record.
    '''

    try:
        drink = Drink.query.filter(Drink.id==drink_id).one_or_none()
        drink.delete()

        return jsonify({
            "success": True,
            "delete": drink_id
        }), 200
    except Exception as e:
        abort(404)


# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': "Internal server error"
    }), 500

@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': "Bad request error"
    }), 400

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found"
    }), 404

@app.errorhandler(AuthError)
def unauthorized_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), 401
