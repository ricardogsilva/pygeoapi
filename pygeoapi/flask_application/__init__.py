"""pygeoapi flask application"""
import flask

from pygeoapi.util import get_api_rules
from pygeoapi.api import API

from pygeoapi.flask_application.pygeoapi_extension import PygeoapiFlaskExtension
from pygeoapi.flask_application.views import (
    admin,
    core,
)


def get_app(pygeoapi_api: API) -> flask.Flask:
    static_folder = 'static'
    if 'templates' in pygeoapi_api.config['server']:
        static_folder = pygeoapi_api.config['server']['templates'].get(
            'static', 'static')
    app = flask.Flask(
        __name__,
        static_folder=static_folder,
        static_url_path='/static',
    )
    api_rules = get_api_rules(pygeoapi_api.config)
    app.url_map.strict_slashes = api_rules.strict_slashes
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = pygeoapi_api.config['server'].get(
        'pretty_print', True)
    if pygeoapi_api.config['server'].get('cors'):
        try:
            from flask_cors import CORS
            CORS(app, CORS_EXPOSE_HEADERS=['*'])
        except ModuleNotFoundError:
            print('Python package flask-cors required for CORS support')
    PygeoapiFlaskExtension(pygeoapi_api, app)
    return app
