from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "CoRider"
app.config['MONGO_URI'] = "mongodb://localhost:27017/Users"
mongo = PyMongo(app)


@app.route('/add', methods=['POST'])
def add_user():
    try:
        _json = request.get_json()
        _name = _json.get('name')
        _email = _json.get('email')
        _password = _json.get('pwd')

        if _name and _email and _password:
            _hashed_password = generate_password_hash(_password)
            user_data = {'name': _name, 'email': _email, 'pwd': _hashed_password}
            result = mongo.db.user.insert_one(user_data)

            resp = jsonify({'message': 'User added', 'id': str(result.inserted_id)})
            resp.status_code = 200
            return resp
        else:
            return jsonify({'message': 'Missing required fields'}), 400
    except Exception as e:
        return jsonify({'message': 'Error occurred', 'error': str(e)}), 500


@app.route('/users', methods=['GET'])
def get_users():
    users = mongo.db.user.find()
    resp = dumps(users)
    return resp


@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    user = mongo.db.user.find_one({'_id': ObjectId(id)})
    resp = dumps(user)
    return resp


@app.route('/user/<id>', methods=['PUT'])
def update_user(id):
    try:
        _json = request.get_json()
        _name = _json.get('name')
        _email = _json.get('email')
        _password = _json.get('pwd')

        if _name and _email and _password:
            _hashed_password = generate_password_hash(_password)
            update_data = {'name': _name, 'email': _email, 'pwd': _hashed_password}
            result = mongo.db.user.update_one({'_id': ObjectId(id)}, {'$set': update_data})

            if result.modified_count > 0:
                resp = jsonify({'message': 'User updated'})
                resp.status_code = 200
                return resp
            else:
                return jsonify({'message': 'User not found'}), 404
        else:
            return jsonify({'message': 'Missing required fields'}), 400
    except Exception as e:
        return jsonify({'message': 'Error occurred', 'error': str(e)}), 500


@app.route('/user/<id>', methods=['DELETE'])
def delete_user(id):
    try:
        result = mongo.db.user.delete_one({'_id': ObjectId(id)})

        if result.deleted_count > 0:
            resp = jsonify({'message': 'User deleted'})
            resp.status_code = 200
            return resp
        else:
            return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'message': 'Error occurred', 'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error=None):
    message = {'status': 404, 'message': 'Not Found - ' + request.url}
    return jsonify(message), 404


if __name__ == "__main__":
    app.run(debug=True)
