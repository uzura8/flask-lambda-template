from flask import Flask
from app.root import bp as root_module
from app.users import bp as users_module

app = Flask(__name__)
app.url_map.strict_slashes = False

app.register_blueprint(users_module)
app.register_blueprint(root_module)
