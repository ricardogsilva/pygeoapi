from pathlib import Path
from typing import Optional

import flask

from pygeoapi.util import get_api_rules
from pygeoapi.api import API
from pygeoapi.admin import Admin
from pygeoapi.flask_application.pygeoapi_extension.views import (
    admin,
    core,
    ogcschemas,
)


class PygeoapiFlaskExtension:

    def __init__(self, pygeoapi_api: API, app: Optional[flask.Flask] = None):
        if app is not None:
            self.init_app(pygeoapi_api, app)

    def init_app(self, pygeoapi_api: API, app: flask.Flask):
        api_rules = get_api_rules(pygeoapi_api.config)
        url_prefix = api_rules.get_url_prefix('flask')
        static_folder = pygeoapi_api.config['server'].get(
            'static_directory',
            Path(__file__).parents[2] / 'static'
        )
        core.configure_blueprint(
            pygeoapi_api,
            static_folder,
            url_prefix
        )
        app.register_blueprint(core.blueprint)
        app.extensions['pygeoapi'] = {
            'api': pygeoapi_api,
            'api_rules': api_rules,
        }
        if pygeoapi_api.config['server'].get('admin'):
            admin_api = Admin(pygeoapi_api.config, pygeoapi_api.openapi)
            admin.configure_blueprint(
                pygeoapi_api,
                admin_api,
                static_folder,
                url_prefix
            )
            app.register_blueprint(admin.blueprint)
            app.extensions['pygeoapi']['admin_api'] = admin_api
        ogc_schemas_location = pygeoapi_api.config['server'].get(
            'ogc_schemas_location')
        if (
                ogc_schemas_location is not None
                and not ogc_schemas_location.startswith('http')
        ):
            app.register_blueprint(ogcschemas.blueprint)
        return app