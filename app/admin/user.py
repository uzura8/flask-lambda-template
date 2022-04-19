import json
from flask import jsonify, request
from app.common.error import InvalidUsage
from app.admin import bp, site_before_request, admin_role_required, ACCEPT_SERVICE_IDS
from flask_cognito import cognito_auth_required, current_user, current_cognito_jwt


@bp.before_request
@site_before_request
def before_request():
    pass


@bp.route('/users', methods=['GET'])
@cognito_auth_required
@admin_role_required
def user_list():
    pass
