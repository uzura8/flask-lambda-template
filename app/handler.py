import os
from flask import Flask, jsonify, request
from werkzeug.routing import Rule
from app.common.error import InvalidUsage
from app.common.decimal_encoder import DecimalEncoder
from app.root import bp as root_module
from app.vote import bp as vote_module
from app.contact import bp as contact_module

cors_accept_origins_str = os.environ.get('CORS_ACCEPT_ORIGINS', '')
CORS_ACCEPT_ORIGINS = cors_accept_origins_str.split(',') if cors_accept_origins_str else []

app = Flask(__name__)
app.url_map.strict_slashes = False
app.json_encoder = DecimalEncoder

app.config['CONTACT_RECAPTCHA_ENABLED'] = \
        os.environ.get('CONTACT_RECAPTCHA_ENABLED', 'False').lower() == 'true'
if app.config['CONTACT_RECAPTCHA_ENABLED']:
    app.config['RECAPTCHA_USE_SSL'] = \
            os.environ.get('CONTACT_RECAPTCHA_USE_SSL', 'False').lower() == 'true'
    app.config['RECAPTCHA_PUBLIC_KEY'] = os.environ.get('CONTACT_RECAPTCHA_PUBLIC_KEY', '')
    app.config['RECAPTCHA_PRIVATE_KEY'] = os.environ.get('CONTACT_RECAPTCHA_PRIVATE_KEY', '')


# get prefix from environment variable
APP_ROOT = os.getenv('APP_ROOT')
if not APP_ROOT is None:
    # define custom_rule class
    class Custom_Rule(Rule):
        def __init__(self, string, *args, **kwargs):
            # check endswith '/'
            if APP_ROOT.endswith('/'):
                prefix_without_end_slash = APP_ROOT.rstrip('/')
            else:
                prefix_without_end_slash = APP_ROOT
            # check startswith '/'
            if APP_ROOT.startswith('/'):
                prefix = prefix_without_end_slash
            else:
                prefix = '/' + prefix_without_end_slash
            super().__init__(prefix + string, *args, **kwargs)

    # set url_rule_class
    app.url_rule_class = Custom_Rule


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.after_request
def add_cors_headers(response):
    response.headers.add('X-Content-Type-Options', 'nosniff')

    r = request.referrer[:-1] if request.referrer else None
    if not CORS_ACCEPT_ORIGINS:
        response.headers.add('Access-Control-Allow-Origin', '*')

    elif r is not None and r in CORS_ACCEPT_ORIGINS:
        response.headers.add('Access-Control-Allow-Origin', r)

    if not CORS_ACCEPT_ORIGINS or r is not None and r in CORS_ACCEPT_ORIGINS:
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Headers', 'Cache-Control')
        response.headers.add('Access-Control-Allow-Headers', 'X-Requested-With')
        response.headers.add('Access-Control-Allow-Headers', 'Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')

    return response


app.register_blueprint(vote_module)
app.register_blueprint(contact_module)
app.register_blueprint(root_module)
