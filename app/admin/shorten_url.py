import json
import traceback
from flask import jsonify, request
from flask_cognito import cognito_auth_required, current_cognito_jwt
from app.models.dynamodb import ShortenUrl, ModelInvalidParamsException
from app.common.error import InvalidUsage
from app.common.string import random_str
from app.common.request import validate_req_params
from app.validators import NormalizerUtils
from app.admin import bp, site_before_request, check_acl_service_id


@bp.before_request
@site_before_request
def before_request():
    pass


@bp.route('/shorten-urls/<string:service_id>', methods=['POST', 'GET'])
@cognito_auth_required
def url_list(service_id):
    service = check_acl_service_id(service_id)

    if request.method == 'POST':
        schema = validation_schema_url_post()
        vals = validate_req_params(schema, request.json)
        vals['serviceId'] = service_id

        created_by = current_cognito_jwt.get('cognito:username', '')
        if created_by:
            vals['createdBy'] = created_by

        url_id = get_new_url_id()
        if not url_id:
            raise InvalidUsage('Create new url_id failed', 500)
        vals['urlId'] = url_id

        try:
            res = ShortenUrl.create(vals)

        except ModelInvalidParamsException as e:
            raise InvalidUsage(e.message, 400)

        except Exception as e:
            print(traceback.format_exc())
            raise InvalidUsage('Server Error', 500)

    else:
        params = {}
        for key in ['count', 'order']:
            params[key] = request.args.get(key)
        vals = validate_req_params(validation_schema_url_list_get(), params)
        #vals = validate_req_params(validation_schema_url_list_get(), request.json)
        key_name =  'lastKeyCreatedAt'
        vals['index'] = 'createdAtGsi'
        last_key = request.args.get('lastKey')
        if last_key:
            params = {key_name:json.loads(last_key)}
            vals_last_key = validate_req_params(validation_schema_url_list_get(), params)
            vals['ExclusiveStartKey'] = vals_last_key[key_name]

        hkey = {'name':'serviceId', 'value': service_id}
        res = ShortenUrl.query_pager(hkey, vals)

    return jsonify(res), 200


@bp.route('/shorten-urls/<string:service_id>/<string:url_id>', methods=['POST', 'GET', 'HEAD', 'DELETE'])
@cognito_auth_required
def url_detail(service_id, url_id):
    validate_req_params(validation_schema_url_id(), {'urlId': url_id})
    query_keys = {'p': {'key':'urlId', 'val':url_id}}
    saved = ShortenUrl.get_one(query_keys)
    if not saved:
        raise InvalidUsage('UrlId does not exist', 404)

    if service_id != saved['serviceId']:
        raise InvalidUsage('ServiceId is invalid', 400)

    service = check_acl_service_id(saved['serviceId'])

    if request.method == 'POST':
        schema = validation_schema_url_post()
        vals = validate_req_params(schema, request.json)
        vals['updatedBy'] = current_cognito_jwt.get('cognito:username', '')

        try:
            saved = ShortenUrl.update(query_keys, vals, True)

        except Exception as e:
            print(traceback.format_exc())
            raise InvalidUsage('Server Error', 500)

    elif request.method == 'DELETE':
        ShortenUrl.delete({'urlId':url_id})
        return jsonify(), 200

    if request.method == 'HEAD':
        return jsonify(), 200

    return jsonify(saved), 200


def get_new_url_id():
    query_keys = {'p': {'key':'urlId'}}
    url_id = ''
    url = ''
    i = 0
    limit = 10
    while not url_id or (url and i < limit):
        url_id = random_str(10)
        query_keys['p']['val'] = url_id
        url = ShortenUrl.get_one(query_keys)
        i += 1

    return url_id


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


def validation_schema_url_post():
    return {
        'url': {
            'type': 'string',
            'coerce': (NormalizerUtils.rtrim),
            'required': True,
            'nullable': False,
            'empty': False,
            'valid_url': True,
        },
        'name': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': False,
            'nullable': True,
            'empty': True,
            'default': '',
        },
        'description': {
            'type': 'string',
            'coerce': (NormalizerUtils.rtrim),
            'required': False,
            'nullable': True,
            'empty': True,
            'default': '',
        },
        'isViaJumpPage': {
            'type': 'boolean',
            'coerce': (str, NormalizerUtils.to_bool),
            'required': False,
            'empty': False,
            'default': False,
        },
    }


def validation_schema_url_list_get():
    return {
        'count': {
            'type': 'integer',
            'coerce': int,
            'required': False,
            'min': 1,
            'max': 50,
            'default': 20,
        },
        'order': {
            'type': 'string',
            'required': False,
            'allowed': ['asc', 'desc'],
            'default': 'desc',
        },
        'lastKeyCreatedAt' : {
            'type': 'dict',
            'schema': {
                'serviceId': {
                    'type': 'string',
                    'required': True,
                    'empty': False,
                },
                'urlId': {
                    'type': 'string',
                    'required': True,
                    'empty': False,
                },
                'createdAt': {
                    'type': 'string',
                    'required': True,
                    'empty': False,
                    'regex': r'\d{4}\-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([\+\-]\d{2}:\d{2}|Z)$',
                },
            }
        },
    }
