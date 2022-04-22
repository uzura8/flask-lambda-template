import os
from functools import wraps
from flask import Blueprint, current_app, jsonify, abort
from flask_cognito import cognito_auth_required, current_cognito_jwt
from app.common.error import InvalidUsage

bp = Blueprint('admin', __name__, url_prefix='/admin')
ACCEPT_SERVICE_IDS = os.environ.get('ACCEPT_SERVICE_IDS', '').split(',')


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


from . import service
from . import user
from . import post
from . import category
from . import tag
