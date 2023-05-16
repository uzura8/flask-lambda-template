import os
from flask import Blueprint, jsonify, request
from app.models.dynamodb import Tag, Service
from app.common.error import InvalidUsage
from app.common.request import validate_req_params
from app.validators import NormalizerUtils

bp = Blueprint('tag', __name__, url_prefix='/tags')


@bp.route('/<string:service_id>', methods=['GET'])
def handle_list(service_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    params = {}
    for key in ['count', 'order']:
        params[key] = request.args.get(key)
    vals = validate_req_params(validation_schema(), params)

    pkeys = {'key':'serviceId', 'val':service_id}
    #body = Tag.get_all_by_pkey(pkeys, vals)
    body = Tag.get_all_by_service_id(service_id, vals)
    return jsonify(body), 200


def validation_schema():
    return {
        'count': {
            'type': 'integer',
            'coerce': int,
            'required': False,
            'min': 1,
            'max': 100,
            'default': 100,
        },
        'order': {
            'type': 'string',
            'required': False,
            'allowed': ['asc', 'desc'],
            'default': 'asc',
        },
    }
