"""pygeoapi flask application"""
import os
from pathlib import Path
from typing import Protocol

import flask

from pygeoapi.api import API
from pygeoapi.conf import PygeoapiConfiguration
from pygeoapi.flask_application.pygeoapi_extension import PygeoapiFlaskExtension
from pygeoapi.openapi import get_oas
from pygeoapi.conf.protocols import ConfigurationManager
from pygeoapi.util import (
    get_api_rules,
    import_object,
)


class ConfigInitializer(Protocol):

    def __call__(self) -> ConfigurationManager:
        """Return an object which implements the pygeoapi configuration interface."""


def get_app(flask_test_config: dict | None = None):
    config_initializer: ConfigInitializer = PygeoapiConfiguration.from_env_variable
    if (config_initializer_path := os.getenv('PYGEOAPI_CONFIG_INITIALIZER')) is not None:
        config_initializer = import_object(config_initializer_path)
    pygeoapi_config = config_initializer()
    openapi_document = get_oas(pygeoapi_config)
    pygeoapi_api = API(pygeoapi_config, openapi_document)
    return get_app_from_pygeoapi_api(pygeoapi_api, flask_test_config)


def get_app_from_pygeoapi_api(
        pygeoapi_api: API,
        flask_test_config: dict | None = None
) -> flask.Flask:
    static_folder = pygeoapi_api.config['server'].get(
        'static_directory',
        Path(__file__).parents[1] / 'static'
    )
    app = flask.Flask(
        __name__,
        static_folder=static_folder,
        static_url_path='/static',
    )
    if flask_test_config is not None:
        app.config.from_mapping(flask_test_config)
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
