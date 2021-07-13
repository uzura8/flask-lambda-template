import os
import boto3
from boto3.dynamodb.conditions import Key
from flask import Flask, jsonify, request

app = Flask(__name__)

USERS_TABLE = os.environ['USERS_TABLE']
IS_LOCAL = bool(os.environ.get('IS_LOCAL'))

if IS_LOCAL:
    dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
else:
    dynamodb = boto3.resource('dynamodb')

@app.route('/')
def index():
    return jsonify({'message': 'Hello World!'})


#@app.route('/<path:path>')
#def any_path(path):
#    return jsonify({'message': 'Here: /' + path})


@app.route('/users/<string:user_id>')
def get_user(user_id):
    table = dynamodb.Table(USERS_TABLE)
    res = table.query(
        KeyConditionExpression=Key('userId').eq(user_id)
    )
    if 'Items' not in res or not res['Items']:
        return jsonify({'error': 'User does not exist'}), 404

    items = res['Items']

    return jsonify(items[0])


@app.route('/users', methods=['POST', 'GET'])
def users():
    table = dynamodb.Table(USERS_TABLE)
    if request.method == 'POST':
        user_id = request.json.get('userId')
        name = request.json.get('name')
        if not user_id or not name:
            return jsonify({'error': 'Please provide userId and name'}), 400

        row = {
            'userId': user_id,
            'name': name
        }
        table.put_item(Item=row)
        return jsonify(row)
    else:
        res = table.scan()
        if 'Items' not in res or not res['Items']:
            return jsonify({'error': 'User does not exist'}), 404
        items = res['Items']

        return jsonify(items)
