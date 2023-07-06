from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "CoRider"
app.config['MONGO_URI'] = "mongodb://localhost:27017/Users"
mongo = PyMongo(app)
api = Api(app)


def endpoint(route):
    def decorator(func):
        app.add_url_rule(route, view_func=func, methods=["GET"])
        app.add_url_rule(route, view_func=func, methods=["POST"])
        app.add_url_rule(route, view_func=func, methods=["PUT"])
        app.add_url_rule(route, view_func=func, methods=["DELETE"])
        return func
    return decorator


class UserResource(Resource):
    @endpoint("/users")
    def get_all_users(self):
        users = list(mongo.db.user.find())
        return jsonify(users)

    @endpoint("/users/<string:user_id>")
    def get_user_by_id(self, user_id):
        user = mongo.db.user.find_one({'_id': ObjectId(user_id)})
        if user:
            return jsonify(user)
        return {'message': 'User not found'}, 404

    @endpoint("/users/<string:user_id>/<int:age>")
    def get_user_by_id_and_age(self, user_id, age):
        user = mongo.db.user.find_one({'_id': ObjectId(user_id), 'age': age})
        if user:
            return jsonify(user)
        return {'message': 'User not found'}, 404

    @endpoint("/users")
    def add_user(self):
        _json = request.get_json()
        _name = _json.get('name')
        _email = _json.get('email')
        _password = _json.get('pwd')

        if _name and _email and _password:
            _hashed_password = generate_password_hash(_password)
            user_data = {'name': _name, 'email': _email, 'pwd': _hashed_password}
            result = mongo.db.user.insert_one(user_data)

            return {'message': 'User added', 'id': str(result.inserted_id)}, 200
        else:
            return {'message': 'Missing required fields'}, 400

    @endpoint("/users/<string:user_id>")
    def update_user(self, user_id):
        _json = request.get_json()
        _name = _json.get('name')
        _email = _json.get('email')
        _password = _json.get('pwd')

        if _name and _email and _password:
            _hashed_password = generate_password_hash(_password)
            update_data = {'name': _name, 'email': _email, 'pwd': _hashed_password}
            result = mongo.db.user.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})

            if result.modified_count > 0:
                return {'message': 'User updated'}, 200
            else:
                return {'message': 'User not found'}, 404
        else:
            return {'message': 'Missing required fields'}, 400

    @endpoint("/users/<string:user_id>")
    def delete_user(self, user_id):
        result = mongo.db.user.delete_one({'_id': ObjectId(user_id)})

        if result.deleted_count > 0:
            return {'message': 'User deleted'}, 200
        else:
            return {'message': 'User not found'}, 404


api.add_resource(UserResource, '/users')


@app.errorhandler(404)
def not_found(error=None):
    message = {'status': 404, 'message': 'Not Found - ' + request.url}
    return jsonify(message), 404


if __name__ == "__main__":
    app.run(debug=True)
