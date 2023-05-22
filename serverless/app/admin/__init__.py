import os
from functools import wraps
from flask import Blueprint, current_app, jsonify, abort, request
from flask_cognito import cognito_auth_required, current_cognito_jwt
from app.common.error import InvalidUsage
from app.models.dynamodb import Service, ServiceConfig, AdminUserConfig

bp = Blueprint('admin', __name__, url_prefix='/admin')


def site_before_request(f):
    def wrapper(*args, **kwargs):
        f(*args, **kwargs)
        #g.locale = str(get_locale())
    return wrapper


def admin_role_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        check_admin_role('admin')

        return f(*args, **kwargs)
    return decorated_function


def admin_role_editor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        role = check_admin_role(['admin', 'editor', 'viewer'])
        if role == 'viewer':
            if request.method in ['POST', 'PUT', 'DELETE']:
                raise InvalidUsage('Forbidden', 403)

        return f(*args, **kwargs)
    return decorated_function


def check_admin_role(accept_roles='admin'):
    if not isinstance(accept_roles, list):
        accept_roles = [accept_roles]

    role = current_cognito_jwt.get('custom:role')
    if role not in accept_roles:
        raise InvalidUsage('Forbidden', 403)

    return role


def check_acl_service_id(service_id, with_configs=False):
    username = current_cognito_jwt.get('cognito:username', '')
    alloweds = AdminUserConfig.get_val(username, 'acceptServiceIds')
    if service_id not in alloweds:
        raise InvalidUsage('Forbidden', 403)

    item = Service.get_one_by_id(service_id)
    if not item:
        raise InvalidUsage('ServiceId does not exist', 404)

    if with_configs:
        item['configs'] = ServiceConfig.get_all_by_service(service_id, True, True, True)

    return item


from . import service
from . import user
from . import post
from . import post_group
from . import category
from . import tag
from . import file
from . import account
from . import shorten_url
