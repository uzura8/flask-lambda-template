import os
from flask import Blueprint, jsonify, request
from app.models.dynamodb import Information
from app.common.error import InvalidUsage
from app.validators import ValidatorExtended, NormalizerUtils
#import time

bp = Blueprint('information', __name__, url_prefix='/informations')
ACCEPT_SERVICE_IDS = os.environ.get('ACCEPT_SERVICE_IDS', '').split(',')


@bp.route('/<string:service_id>', methods=['POST', 'GET'])
def informations(service_id):
    if service_id not in ACCEPT_SERVICE_IDS:
        raise InvalidUsage('ServiceId does not exist', 404)

    if request.method == 'POST':
        schema = validation_schema_informations_post()
        vals = validate_req_params(schema, request.json)
        item = Information.get_one_by_slug(service_id, vals['slug'])
        if item:
            raise InvalidUsage('Slug already used', 400)

        #time.sleep(1)
        body = Information.create(service_id, vals)

    else:
        params = {'publish': True}
        for key in ['limit', 'order', 'sinceTime', 'untilTime']:
            params[key] = request.args.get(key)
        schema = validation_schema_informations_post()
        vals = validate_req_params(schema, params)
        body = Information.query_all('gsi-list-all', service_id, vals)

    return jsonify(body), 200


@bp.route('/<string:service_id>/<string:slug>', methods=['POST', 'GET', 'HEAD'])
def information(service_id, slug):
    if service_id not in ACCEPT_SERVICE_IDS:
        raise InvalidUsage('ServiceId does not exist', 404)

    item = Information.get_one_by_slug(service_id, slug)
    if not item:
        raise InvalidUsage('Not Found', 404)

    if request.method == 'POST':
        pass

    if request.method == 'HEAD':
        return jsonify(), 200

    return jsonify(item), 200


def validation_schema_informations_post():
    return {
        'slug': {
            'type': 'string',
            'coerce': (str, NormalizerUtils.trim),
            'required': True,
            'empty': False,
            'maxlength': 128,
            'regex': r'^[0-9a-z\-]+$',
        },
        'title': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': True,
            'empty': False,
        },
        'body': {
            'type': 'string',
            'coerce': (NormalizerUtils.rtrim),
            'required': False,
            'nullable': True,
            'empty': True,
            'default': '',
        },
        'categoryId': {
            'type': 'string',
            'coerce': (NormalizerUtils.rtrim),
            'required': True,
            'empty': False,
        },
        'publish': {
            'type': 'boolean',
            'coerce': (str, NormalizerUtils.to_bool),
            'required': False,
            'empty': True,
            'default': False,
        },
        'publishAt': {
            'type': 'string',
            'coerce': (NormalizerUtils.rtrim),
            'required': False,
            'empty': True,
            'regex': r'\d{4}\-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([\+\-]\d{2}:\d{2}|Z)$',
        },
        'limit': {
            'type': 'integer',
            'coerce': int,
            'required': False,
            'min': 1,
            'max': 50,
            'default': 5,
        },
        'order': {
            'type': 'string',
            'required': False,
            'allowed': ['asc', 'desc'],
            'default': 'desc',
        },
        'sinceTime': {
            'type': 'string',
            'coerce': (NormalizerUtils.rtrim),
            'required': False,
            'nullable': True,
            'empty': True,
            'regex': r'\d{4}\-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([\+\-]\d{2}:\d{2}|Z)$',
        },
        'untilTime': {
            'type': 'string',
            'coerce': (NormalizerUtils.rtrim),
            'required': False,
            'nullable': True,
            'empty': True,
            'regex': r'\d{4}\-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([\+\-]\d{2}:\d{2}|Z)$',
        },
    }


def validate_req_params(schema, params=None):
    target_schema = {}
    target_vals = {}
    if params:
        for key, val in params.items():
            if key in schema:
                target_schema[key] = schema[key]
                target_vals[key] = val

    v = ValidatorExtended(target_schema)
    if not v.validate(target_vals):
        msg = 'Validation Failed'
        field_errs = []
        err_dict = v.errors
        for key, errs in err_dict.items():
            for err in errs:
                field_errs.append({
                    'field': key,
                    'message': err,
                })

        raise InvalidUsage(msg, 400, {'errors': field_errs})

    return v.document
