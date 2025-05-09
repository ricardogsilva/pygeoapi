import dataclasses
from pathlib import Path
from typing import Optional

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import (
    Mount,
    Route,
)
from starlette.staticfiles import StaticFiles

from pygeoapi.api import API
from pygeoapi.admin import Admin
from pygeoapi.config import get_config
from pygeoapi.openapi import load_openapi_document
from pygeoapi.starlette_application import (
    admin,
    core,
)
from pygeoapi.starlette_application.middleware import ApiRulesMiddleware
from pygeoapi.util import get_api_rules


@dataclasses.dataclass
class PygeoapiStarletteState:
    api: API
    admin_api: Optional[Admin] = None


def get_app():
    pygeoapi_config = get_config()
    openapi_document = load_openapi_document()
    pygeoapi_api = API(pygeoapi_config, openapi_document)
    return get_app_from_pygeoapi_api(pygeoapi_api)


def get_app_from_pygeoapi_api(pygeoapi_api: API) -> Starlette:
    provided_static_dir = (
        pygeoapi_api.config['server'].get('templates', {}).get('static')
    )
    if provided_static_dir is not None:
        static_dir = Path(provided_static_dir)
    else:
        static_dir = Path(__file__).parents[1].resolve() / 'static'
    api_rules = get_api_rules(pygeoapi_api.config)
    url_prefix = api_rules.get_url_prefix('starlette')
    routes = [
        Mount(f'{url_prefix}/static', StaticFiles(directory=static_dir)),
        Mount(url_prefix or '/', routes=core.routes)
    ]
    admin_api = None
    if pygeoapi_api.config['server'].get('admin'):
        admin_api = Admin(pygeoapi_api.config, pygeoapi_api.openapi)
        routes.append(
            Mount('/admin', routes=admin.routes)
        )
    if url_prefix:
        # If a URL prefix is in effect, Flask allows the static resource URLs
        # to be written both with or without that prefix (200 in both cases).
        # Starlette does not allow this, so for consistency we'll add a static
        # mount here WITHOUT the URL prefix (due to router order).
        routes.append(Mount('/static', StaticFiles(directory=static_dir)))

    ogc_schemas_location = pygeoapi_api.config['server'].get(
        'ogc_schemas_location')
    if (
            ogc_schemas_location is not None
            and not ogc_schemas_location.startswith('http')
    ):
        schemas_path = Path(ogc_schemas_location)
        if not schemas_path.exists():
            raise RuntimeError('OGC schemas misconfigured')
        routes.append(
            Route(f'{url_prefix}/schemas', StaticFiles(directory=schemas_path))
        )

    middleware = []
    # CORS: optionally enable from config.
    if pygeoapi_api.config['server'].get('cors', False):
        middleware.append(
            Middleware(
                CORSMiddleware,
                allow_origins=['*'],
                allow_methods=['*'],
                expose_headers=['*']
            )
        )
    if api_rules.strict_slashes:
        middleware.append(
            Middleware(
                ApiRulesMiddleware,
                url_prefix=url_prefix,
                use_strict_slashes=api_rules.strict_slashes
            )
        )

    app = Starlette(
        debug=pygeoapi_api.config['server'].get('debug', False),
        routes=routes,
        middleware=middleware,
    )
    if api_rules.strict_slashes:
        app.router.redirect_slashes = False

    app.state.PYGEOAPI = PygeoapiStarletteState(
        api=pygeoapi_api,
        admin_api=admin_api,
    )
    return app