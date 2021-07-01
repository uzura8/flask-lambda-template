from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return jsonify({'message': 'Hello World!'})


@app.route('/<path:path>')
def any_path(path):
    return jsonify({'message': 'Here: /' + path})
