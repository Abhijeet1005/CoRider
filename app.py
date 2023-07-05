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


class UserResource(Resource):
    def get(self, user_id=None):
        if user_id:
            user = mongo.db.user.find_one({'_id': ObjectId(user_id)})
            if user:
                return jsonify(user)
            return {'message': 'User not found'}, 404

        users = list(mongo.db.user.find())  # Convert the cursor to a list
        return jsonify(users)

    def post(self):
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

    def put(self, user_id):
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

    def delete(self, user_id):
        result = mongo.db.user.delete_one({'_id': ObjectId(user_id)})

        if result.deleted_count > 0:
            return {'message': 'User deleted'}, 200
        else:
            return {'message': 'User not found'}, 404


api.add_resource(UserResource, '/users', '/users/<string:user_id>')


@app.errorhandler(404)
def not_found(error=None):
    message = {'status': 404, 'message': 'Not Found - ' + request.url}
    return jsonify(message), 404


if __name__ == "__main__":
    app.run(debug=True)
