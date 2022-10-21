import os
from functools import wraps
from flask import Blueprint, current_app, jsonify, abort
from flask_cognito import cognito_auth_required, current_cognito_jwt
from app.common.error import InvalidUsage
from app.models.dynamodb import Service

bp = Blueprint('admin', __name__, url_prefix='/admin')


def site_before_request(f):
    def wrapper(*args, **kwargs):
        f(*args, **kwargs)
        #g.locale = str(get_locale())
    return wrapper


def admin_role_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_cognito_jwt.get('custom:role') != 'admin':
            raise InvalidUsage('Forbidden', 403)

        return f(*args, **kwargs)
    return decorated_function


def check_acl_service_id(service_id):
    alloweds = current_cognito_jwt.get('custom:acceptServiceIds', '').split(',')
    if service_id not in alloweds:
        raise InvalidUsage('Forbidden', 403)

    item = Service.get_one_by_id(service_id)
    if not item:
        raise InvalidUsage('ServiceId does not exist', 404)

    return item


from . import service
from . import user
from . import post
from . import post_group
from . import category
from . import tag
from . import file
from . import account
