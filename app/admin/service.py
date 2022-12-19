import json
import os
from flask import jsonify, request
from flask_cognito import cognito_auth_required
from app.models.dynamodb import Service, ServiceConfig
from app.common.error import InvalidUsage
from app.common.request import validate_req_params
from app.validators import NormalizerUtils
from app.admin import bp, site_before_request, admin_role_required

AVAILABLE_FUNCTIONS = json.loads(os.environ.get('AVAILABLE_FUNCTIONS'))


@bp.before_request
@site_before_request
def before_request():
    pass


@bp.route('/services', methods=['POST', 'GET'])
@cognito_auth_required
@admin_role_required
def service_list():
    services = Service.scan()
    services = sorted(services, key=lambda x: x['serviceId'])
    if request.method == 'POST':
        vals = validate_req_params(validation_schema_services(), request.json)
        if next((x for x in services if x['serviceId'] == vals['serviceId']), None):
            raise InvalidUsage('ServiceId already used', 400)
        service = Service.create(vals)
        return service

    return jsonify(services), 200


@bp.route('/services/<string:service_id>', methods=['POST', 'GET'])
@cognito_auth_required
@admin_role_required
def service_detail(service_id):
    key = {'p': {'key':'serviceId', 'val':service_id}}
    service = Service.get_one(key)
    if not service:
        raise InvalidUsage('ServiceId does not exist', 404)

    if request.method == 'POST':
        alloweds = ['label', 'functions', 'configs']
        vals = validate_req_params(validation_schema_services(), request.json, alloweds)
        configs = None
        if 'configs' in vals:
            configs = vals.pop('configs')

        updated = Service.update(key, vals, True)

        saved_confs = {}
        if configs is not None and any(configs):
            for key, val in configs.items():
                name = ServiceConfig.conv_key_to_save_name(key)
                if not name:
                    continue
                res = ServiceConfig.save(service_id, name, val)
                saved_confs[key] = res['configVal']
        updated['configs'] = saved_confs

        return jsonify(updated), 200

    service['configs'] = ServiceConfig.get_all_by_service(service_id, True)
    return jsonify(service), 200


def validation_schema_services():
    return {
        'serviceId': {
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
        'functions': {
            'type': 'list',
            'required': False,
            'empty': True,
            'default': [],
            'allowed': AVAILABLE_FUNCTIONS
        },
        'body': {
            'type': 'string',
            'coerce': (NormalizerUtils.rtrim),
            'required': False,
            'nullable': True,
            'empty': True,
            'default': '',
        },
        'frontendPostDetailUrlPrefix': {
            'type': 'string',
            'coerce': (NormalizerUtils.rtrim),
            'valid_url': True,
            'required': False,
            'nullable': True,
            'empty': True,
            'default': '',
        },
        'configs' : {
            'type': 'dict',
            'required': False,
            'empty': True,
            'schema': {
                'jumpPageUrl': {
                    'type': 'string',
                    'required': False,
                    'empty': True,
                },
                'jumpPageParamKey': {
                    'type': 'string',
                    'required': False,
                    'empty': True,
                },
            }
        },
    }
