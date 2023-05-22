import os
from flask import Blueprint, jsonify
from app.models.dynamodb import ShortenUrl
from app.common.error import InvalidUsage
from app.common.request import validate_req_params
from app.validators import NormalizerUtils

bp = Blueprint('shorten_url', __name__, url_prefix='/shorten-urls')


@bp.route('/<string:url_id>', methods=['GET'])
def shorten_url_detail(url_id):
    vals = validate_req_params(validation_schema_url_id(), {'urlId':url_id})
    item = ShortenUrl.get_one_by_pkey('urlId', vals['urlId'])
    if not item:
        raise InvalidUsage('urlId does not exist', 404)

    return jsonify(ShortenUrl.to_response(item)), 200


def validation_schema_url_id():
    return {
        'urlId': {
            'type': 'string',
            'coerce': (str, NormalizerUtils.trim),
            'required': True,
            'empty': False,
            'maxlength': 10,
            'regex': r'^[0-9a-zA-Z]{10}$',
        }
    }
