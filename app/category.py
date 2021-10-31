import os
from flask import Blueprint, jsonify, request
from app.models.dynamodb import Category
from app.common.error import InvalidUsage
from app.common.request import validate_req_params
from app.validators import NormalizerUtils

bp = Blueprint('category', __name__, url_prefix='/categories')
ACCEPT_SERVICE_IDS = os.environ.get('ACCEPT_SERVICE_IDS', '').split(',')


@bp.route('/<string:service_id>', methods=['POST', 'GET'])
def handle_list(service_id):
    if service_id not in ACCEPT_SERVICE_IDS:
        raise InvalidUsage('ServiceId does not exist', 404)

    if request.method == 'POST':
        vals = validate_req_params(validation_schema(), request.json)
        item = Category.get_one_by_slug(service_id, vals['slug'])
        if item:
            raise InvalidUsage('Slug already used', 400)

        body = Category.create(service_id, vals)

    else:
        pass

    return jsonify(body), 200


@bp.route('/<string:service_id>/<string:slug>', methods=['POST', 'GET', 'HEAD'])
def handle_detail(service_id, slug):
    if service_id not in ACCEPT_SERVICE_IDS:
        raise InvalidUsage('ServiceId does not exist', 404)
    vals = validate_req_params(validation_schema(), {'slug':slug})
    item = Category.get_one_by_slug(service_id, vals['slug'], True)
    if not item:
        raise InvalidUsage('Not Found', 404)

    if request.method == 'POST':
        pass

    if request.method == 'HEAD':
        return jsonify(), 200

    return jsonify(item), 200


def validation_schema():
    return {
        'slug': {
            'type': 'string',
            'coerce': (str, NormalizerUtils.trim),
            'required': True,
            'empty': False,
            'maxlength': 128,
            'regex': r'^[0-9a-z\-]+$',
        },
        'label': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': True,
            'empty': False,
        },
        'parentId': {
            'type': 'integer',
            'coerce': int,
            'required': True,
            'nullable': False,
            'empty': False,
        },
    }
