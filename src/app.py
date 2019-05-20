from flask import Flask, jsonify, request, make_response
from models.items import Item
from models.users import User
from models.shared import db
from functools import wraps
import datetime
import jwt
from werkzeug.security import check_password_hash

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../shop_api.db'
app.config['SECRET_KEY'] = 'secretkey'

db.init_app(app)


def require_token(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if "token" in request.headers and request.headers["token"]:
            token = request.headers["token"]
            try:
                jwt_data = jwt.decode(token, key=app.config['SECRET_KEY'])
                user = User.find_one(jwt_data["id"])
                return f(user, *args, **kwargs)
            except:
                return jsonify({"message": "Invalid Token"})

        else:
            return jsonify({"message": "No token found [token: <token string>]"})

    return decorator


@app.route("/api/v1/auth/login", methods=['POST'])
def login():
    try:
        r = request.json
        user = User.find_by_username(r["username"])
        # user_class = User.find_userclass_by_username(r["username"])
        user["exp"] = datetime.datetime.utcnow() + datetime.timedelta(minutes=20)
        if check_password_hash(user["password"], r["password"]) and user["admin"] is 1:
            token = jwt.encode(payload=user, key=app.config['SECRET_KEY'])
            return jsonify({"token": token.decode('UTF-8')})
        elif check_password_hash(user["password"], r["password"]) and user["admin"] is 0:
            token = jwt.encode(payload=user, key=app.config['SECRET_KEY'])
            return jsonify({"token": token.decode('UTF-8')})
        else:
            return make_response("Login Failed!", 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
    except:
        return make_response("Login Failed!", 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})


@app.route("/api/v1/user", methods=['GET'])
@require_token
def get_users(current_user):
    if current_user["admin"] is 0:
        return jsonify({"message": "You are not authorised to perform this function"})
    try:
        user = User.view()
        return jsonify({'user': user})
    except:
        return jsonify({"message": "An error occurred when getting users"})


@app.route("/api/v1/user/<id>", methods=['GET'])
@require_token
def get_one_user(current_user, id):
    if current_user["admin"] is 0:
        return jsonify({"message": "You are not authorised to perform this function"})
    try:
        user = User.find_one(id)
        return jsonify({'user': user})
    except:
        return jsonify({"message": "An error occurred when getting user"})


@app.route("/api/v1/user", methods=['POST'])
@require_token
def insert_user(current_user):
    if current_user["admin"] is 0:
        return jsonify({"message": "You are not authorised to perform this function"})
    try:
        response = request.json
        User.create(response["username"], response["password"])
        return jsonify({'message': '{} has been created'.format(response["username"])})
    except:
        return jsonify({"message": "An error occurred, User could not be created"})


@app.route("/api/v1/user/<id>", methods=['PUT'])
@require_token
def update_user(current_user, id):
    if current_user["admin"] is 0:
        return jsonify({"message": "You are not authorised to perform this function"})
    try:
        response = request.json
        username = password = admin = None
        if "username" in response:
            username = response["username"]
        if "password" in response:
            password = response["password"]
        if "admin" in response:
            admin = response["admin"]
        User.update(id, username, password, admin)
        return jsonify({'message': 'User has been updated'})
    except:
        return jsonify({"message": "An error occurred, User could not be updated"})


@app.route("/api/v1/user/<id>", methods=['DELETE'])
@require_token
def delete_user(current_user, id):
    if current_user["admin"] is 0:
        return jsonify({"message": "You are not authorised to perform this function"})
    try:
        user = User.find_one(id)
        if not user:
            return jsonify({"message": "User does not exist"})
        User.delete(id)
        return jsonify({"message": "User has been deleted"})
    except:
        return jsonify({"message: Unable to delete user. An error occurred"})


@app.route("/api/v1/item", methods=['GET'])
def get_items():
    try:
        items = Item.view()
        return jsonify({"items": items})
    except:
        return jsonify({"message": "An error occurred when getting items"})


@app.route("/api/v1/item/<id>", methods=['GET'])
def get_one_item(id):
    try:
        item = Item.find_one(id)
        return jsonify({"item": item})
    except:
        return jsonify({"message": "An error occurred when getting item"})


@app.route("/api/v1/item", methods=['POST'])
@require_token
def insert_item(current_user):
    if current_user["admin"] is 0:
        return jsonify({"message": "You are not authorised to perform this function"})
    try:
        r = request.json
        Item.create(r['name'], r['description'], r['type'], r['price'], current_user['id'], r['quantity'])
        return jsonify({"message": "{} has been created".format(r['name'])})
    except:
        return jsonify({"message": "An error occurred, Item could not be created"})


@app.route("/api/v1/item/<id>", methods=['PUT'])
@require_token
def update_item(current_user, id):
    if current_user["admin"] is 0:
        return jsonify({"message": "You are not authorised to perform this function"})
    try:
        response = request.json
        Item.update(id, response)
        return jsonify({"message": "Item has been updated"})
    except:
        return jsonify({"message": "An error occurred, Item could not be updated"})


@app.route("/api/v1/item/<id>", methods=['DELETE'])
@require_token
def delete_item(current_user, id):
    if current_user["admin"] is 0:
        return jsonify({"message": "You are not authorised to perform this function"})
    try:
        item = Item.find_one(id)
        if not item:
            return jsonify({"message": "Item not found"})
        Item.delete(id)
        return jsonify({"message": "{} successfully deleted".format(item["name"])})
    except:
        return jsonify({"message": "An error occurred, Item could not be deleted"})


@app.route("/api/v1/item/buy/<id>", methods=['PUT'])
def buy_item(id):
    try:
        if request.data and "quantity" in request.json:
            quantity = request.json["quantity"]
        else:
            quantity = 1
        Item.buy(id, quantity)
        return jsonify({"message": "Item has been bought"})
    except:
        return jsonify({"message": "An error occurred, Item could not be purchased"})


if __name__ == '__main__':
    app.run(debug=True)
