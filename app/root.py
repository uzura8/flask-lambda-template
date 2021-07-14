from flask import Blueprint, jsonify

bp = Blueprint('root', __name__)


@bp.route('/')
def index():
    return jsonify({'message': 'Hello World!'})


@bp.route('/<path:path>')
def any_path(path):
    return jsonify({'message': 'Here: /' + path})
