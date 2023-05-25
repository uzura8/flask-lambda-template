import os
from flask import Blueprint, jsonify, request
from app.models.dynamodb import ShortenUrl, ShortenUrlDomain, Service
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


@bp.route('/<string:service_id>/domains', methods=['GET'])
def shorten_url_domains(service_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    params = {'isList':request.args.get('isList')}
    vals = validate_req_params(validation_schema_get_domains(), params)
    is_list_response = vals.get('isList')

    keys = {'p':{'key':'serviceId', 'val':service_id}}
    domains = ShortenUrlDomain.get_all(keys, False, 'serviceIdIndex')

    if is_list_response:
        response = [ item['domain'] for item in domains ]
    else:
        response = [ ShortenUrlDomain.to_response(item) for item in domains ]

    return jsonify(response), 200


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


def validation_schema_get_domains():
    return {
        'isList': {
            'type': 'boolean',
            'coerce': (str, NormalizerUtils.to_bool),
            'required': False,
            'empty': True,
            'default': False,
        },
    }
