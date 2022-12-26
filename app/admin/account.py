from flask import jsonify
from flask_cognito import cognito_auth_required, current_cognito_jwt
from app.models.dynamodb import Service
from app.admin import bp, site_before_request, admin_role_editor_required


@bp.before_request
@site_before_request
def before_request():
    pass


@bp.route('/account/services', methods=['GET'])
@cognito_auth_required
@admin_role_editor_required
def account_service_list():
    accept_sids = current_cognito_jwt.get('custom:acceptServiceIds').split(',')
    if not accept_sids:
        return jsonify([]), 200

    services = Service.scan()
    services = filter(lambda x: x['serviceId'] in accept_sids, services)
    services = sorted(services, key=lambda x: x['serviceId'])
    return jsonify(services), 200
