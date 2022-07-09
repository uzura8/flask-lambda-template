from flask import jsonify, request
from flask_cognito import cognito_auth_required
from app.models.dynamodb import Service
from app.common.error import InvalidUsage
from app.common.request import validate_req_params
from app.validators import NormalizerUtils
from app.admin import bp, site_before_request, admin_role_required


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
        vals = validate_req_params(validation_schema_services(), request.json, ['label'])
        updated = Service.update(key, vals, True)
        return jsonify(updated), 200
    else:
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
        'body': {
            'type': 'string',
            'coerce': (NormalizerUtils.rtrim),
            'required': False,
            'nullable': True,
            'empty': True,
            'default': '',
        },
    }
