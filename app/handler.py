import os
from flask import Flask
from werkzeug.routing import Rule
from app.common.decimal_encoder import DecimalEncoder
from app.root import bp as root_module
from app.vote import bp as vote_module

app = Flask(__name__)
app.url_map.strict_slashes = False
app.json_encoder = DecimalEncoder

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

app.register_blueprint(vote_module)
app.register_blueprint(root_module)
