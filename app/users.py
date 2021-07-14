import os
from flask import Blueprint, jsonify, request
from boto3.dynamodb.conditions import Key
from dynamodb import dynamodb

bp = Blueprint('users', __name__, url_prefix='/users')

TABLE_NAME = 'users'
USERS_TABLE = '-'.join([os.environ['PRJ_PREFIX'], TABLE_NAME])


@bp.route('/<string:user_id>')
def get_user(user_id):
    table = dynamodb.Table(USERS_TABLE)
    res = table.query(
        KeyConditionExpression=Key('userId').eq(user_id)
    )
    if 'Items' not in res or not res['Items']:
        return jsonify({'error': 'User does not exist'}), 404

    items = res['Items']

    return jsonify(items[0])


@bp.route('/', methods=['POST', 'GET'])
def users():
    table = dynamodb.Table(USERS_TABLE)
    if request.method == 'POST':
        user_id = request.json.get('userId')
        name = request.json.get('name')
        if not user_id or not name:
            return jsonify({'error': 'Please provide userId and name'}), 400

        item = {
            'userId': user_id,
            'name': name
        }
        table.put_item(Item=item)
    else:
        res = table.scan()
        if 'Items' not in res or not res['Items']:
            return jsonify({'error': 'User does not exist'}), 404
        item = res['Items']

    return jsonify(item)
