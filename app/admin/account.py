from flask import jsonify, request
from flask_cognito import cognito_auth_required, current_cognito_jwt
from app.models.dynamodb import Service
from app.common.error import InvalidUsage
from app.common.request import validate_req_params
from app.validators import NormalizerUtils
from app.admin import bp, site_before_request


@bp.before_request
@site_before_request
def before_request():
    pass


@bp.route('/account/services', methods=['GET'])
@cognito_auth_required
def account_service_list():
    accept_sids = current_cognito_jwt.get('custom:acceptServiceIds').split(',')
    if not accept_sids:
        return jsonify([]), 200

    services = Service.scan()
    services = filter(lambda x: x['serviceId'] in accept_sids, services)
    services = sorted(services, key=lambda x: x['serviceId'])
    return jsonify(services), 200
