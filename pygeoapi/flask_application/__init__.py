"""pygeoapi flask application"""
from pathlib import Path

import flask

from pygeoapi.api import API
from pygeoapi.config import get_config
from pygeoapi.flask_application.pygeoapi_extension import PygeoapiFlaskExtension
from pygeoapi.openapi import load_openapi_document
from pygeoapi.util import get_api_rules


def get_app():
    pygeoapi_config = get_config()
    openapi_document = load_openapi_document()
    pygeoapi_api = API(pygeoapi_config, openapi_document)
    return get_app_from_pygeoapi_api(pygeoapi_api)


def get_app_from_pygeoapi_api(pygeoapi_api: API) -> flask.Flask:
    static_folder = pygeoapi_api.config['server'].get(
        'static_directory',
        Path(__file__).parents[1] / 'static'
    )
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
