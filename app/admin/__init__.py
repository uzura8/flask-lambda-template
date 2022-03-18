import os
from flask import Blueprint, current_app
from flask_cognito import CognitoAuth

bp = Blueprint('admin', __name__, url_prefix='/admin')
ACCEPT_SERVICE_IDS = os.environ.get('ACCEPT_SERVICE_IDS', '').split(',')


def site_before_request(f):
    def wrapper(*args, **kwargs):
        f(*args, **kwargs)
        #g.locale = str(get_locale())
    return wrapper


from . import post
from . import category
from . import tag
