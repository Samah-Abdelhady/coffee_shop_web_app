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

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# def create_app(test_config=None):
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE,PATCH')
    return response
## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drink = Drink.query.order_by(Drink.id).all()

    if len(drink) == 0:
      abort(404)

    drinks = []
    for d in drink:
        all_drinks = d.short()
        drinks.append(all_drinks)

    return jsonify({
      'status_code': 200,
      'success': True,
      'drinks': drinks
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks_detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drink = Drink.query.order_by(Drink.id).all()
    if len(drink) == 0:
      abort(404)

    drinks = []
    for d in drink:
        all_drinks = d.long()
        drinks.append(all_drinks)

    return jsonify({
      'status_code': 200,
      'success': True,
      'drinks': drinks
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks_detail', methods=['POST'])
@requires_auth('post:drinks')
def post_new_drink(payload):
    body = request.get_json()
    new_title = body.get('title', "")
    new_recipe = body.get('recipe', "")

    if((new_title=="") or (new_recipe=="")):
        abort(400)

    drink = Drink(title=new_title, recipe=new_recipe)
    drink.insert()

    latest_drink = Drink.query.filter(Drink.title == new_title).one()
    latest_drink = latest_drink.long()
    drinks = []
    drinks.append(latest_drink)
    return jsonify({
        'status_code': 200,
        'success': True,
        'drinks': drinks
        })

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(404)
    # else:
    body = request.get_json()
    new_title = body.get('title', "")
    new_recipe = body.get('recipe', "")

    if((new_title=="") or (new_recipe=="")):
        abort(400)
        # else:
    drink.title = new_title
    drink.recipe = new_recipe
    drink.update()

    latest_drink = Drink.query.filter(Drink.id == drink_id).one()
    latest_drink = latest_drink.long()
    drinks = []
    drinks.append(latest_drink)
    return jsonify({
        'status_code': 200,
        'success': True,
        'drinks': drinks
        })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(404)
    else:
        drink.delete()

    return jsonify({
        'status_code': 200,
        'success': True,
        'delete': drink_id
        })

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
     "success": False,
     "error": 500,
     "message": "internal server error"
     }), 500
'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler('AuthError')
def un_athorized(error):
    return jsonify({
      "success": False, 
      "error": "AuthError",
      "message": "authorization Error"
      }), 'AuthError'