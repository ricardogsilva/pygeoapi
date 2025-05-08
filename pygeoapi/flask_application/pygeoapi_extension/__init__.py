from typing import Optional

import flask

from pygeoapi.util import get_api_rules
from pygeoapi.api import API
from pygeoapi.flask_application.pygeoapi_extension.views import core


class PygeoapiFlaskExtension:

    def __init__(self, pygeoapi_api: API, app: Optional[flask.Flask] = None):
        if app is not None:
            self.init_app(pygeoapi_api, app)

    def init_app(self, pygeoapi_api: API, app: flask.Flask):
        # get the pygeoapi config from flask config

        static_folder = 'static'
        if 'templates' in pygeoapi_api.config['server']:
            static_folder = pygeoapi_api.config['server']['templates'].get(
                'static', 'static')

        api_rules = get_api_rules(pygeoapi_api.config)
        app.extensions['pygeoapi'] = {
            'api': pygeoapi_api,
            'api_rules': api_rules,
        }
        url_prefix = api_rules.get_url_prefix('flask')
        core.configure_blueprint(static_folder, url_prefix)
        app.register_blueprint(core.blueprint)
        return app