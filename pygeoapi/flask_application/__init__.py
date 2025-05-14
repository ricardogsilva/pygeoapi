"""pygeoapi flask application"""
import os
from pathlib import Path

import flask

from pygeoapi.api import API
from pygeoapi.conf import PygeoapiConfiguration
from pygeoapi.flask_application.pygeoapi_extension import PygeoapiFlaskExtension
from pygeoapi.openapi import get_oas
from pygeoapi.util import get_api_rules


def get_app():
    if (config_path := os.getenv('PYGEOAPI_CONFIG')) is not None:
        pygeoapi_config = PygeoapiConfiguration.from_configuration_file(config_path)
        openapi_document = get_oas(pygeoapi_config)
        pygeoapi_api = API(pygeoapi_config, openapi_document)
        return get_app_from_pygeoapi_api(pygeoapi_api)
    else:
        raise RuntimeError('PYGEOAPI_CONFIG environment variable not set')


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
