import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
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

# ROUTES
# get the drinks from the client


@app.route("/drinks", methods=["GET"])
def get_drinks():
    return jsonify({"success": True,
                    "drinks": [drink.short() for drink in drinks_dis]}), 200

# get all the details concerning the drinks from the client


@app.route("/drinks-detail", methods=["GET"])
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    drinks_dis = Drink.query.all()
    return jsonify({"success": True,
                    "drinks": [drink.long() for drink in drinks_dis]}), 200

# Add drinks to the list of existing drinks list


@app.route("/drinks", methods=["POST"])
@requires_auth('post:drinks')
def add_drinks():
    data = request.get_json()
    title = data.get("title", None)
    recipe = data.get("recipe", None)
    if not (title or recipe):
        return jsonify({
                "success": False,
                "error": 400,
                "message": "Title or recipe missing"
                }), 400
# print("the data is", data)
    drink = Drink(title=title, recipe=json.dumps(recipe))
    drink.insert()
    return jsonify({"success": True, "drinks": [drink.long()]})

# update a particular drink specifications


@app.route("/drinks/<id>", methods=["PATCH"])
@requires_auth('patch:drinks')
def update_drink(id):
    data = request.get_json()
    drink = Drink.query.filter_by(id=id).first()
    if not drink:
        return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404
    drink.title = data.get("title")
    drink.recipe = json.dumps(data.get("recipe"))
    drink.update()
    # if (drinks_dis_detail not in drinks):
    #     abort(404)
    return jsonify({"success": True, "drinks": [drink.long()]}), 200


# Remove a drink or drinks from the list of drinks
@app.route("/drinks/<id>", methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(id):
    drink = Drink.query.filter_by(id=id).first()
    if not drink:
        return jsonify({"success": False,
                        "error": 404,
                        "message": "resource not found"}), 404
    drink.delete()
    return jsonify({"success": True, "delete": id}), 200

# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def notfound(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404


@app.errorhandler(AuthError)
def Auth_Error(error):
    return jsonify({
                    "success": False,
                    "error": AuthError,
                    "message": "Sorry, there's an authentification error"
                    }), AuthError
