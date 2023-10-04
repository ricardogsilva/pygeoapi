"""Pygeoapi Flask integration.

This module defines two flask-related objects:

- PyGeoApiFlaskExtension - a Flask extension that can be used in order to
  provide pygeoapi functionality to a (potentially third-party) Flask
  application

- app - pygeoapi's official Flask application, which is created using the
  recommended factory pattern


Run pygeoapi dev web server like this:

FLASK_DEBUG=true \
FLASK_APP="./pygeoapi.rfc2.flask_app.app:create_app" \
FLASK_RUN_PORT=8000 \
FLASK_PYGEOAPI_OGC_API_SCHEMAS_BASE_DIR=<schemas_base_dir> \
flask run

Run the CLI like this:

FLASK_DEBUG=true \
FLASK_APP="./pygeoapi.rfc2.flask_app.app:create_app" \
FLASK_RUN_PORT=8000 \
FLASK_PYGEOAPI_OGC_API_SCHEMAS_BASE_DIR=<schemas_base_dir> \
flask pygeoapi --help

"""
import logging
from pathlib import Path
from typing import Callable

import flask

from .. import core
from .pygeoapi_blueprint import blueprint as pygeoapi_blueprint
from .pygeoapi_blueprint import (
    commands,
    views,
)


def flask_pygeoapi_url_resolver(pygeoapi_method, *args, **kwargs):
    """A URL resolver for pygeoapi."""
    api: core.Api = flask.current_app.extensions["pygeoapi"]["api"]
    route_mapping = {
        api.get_landing_page: "pygeoapi.get_landing_page",
        api.list_processes: "pygeoapi.list_processes",
    }
    return flask.url_for(route_mapping[pygeoapi_method])


class PyGeoApiFlaskExtension:
    """Flask extension for pygeoapi.

    Can be used on any flask application by doing:

    >>> app = create_app()  # or whatever way you create your flask app
    >>> pygeoapi_extension = PyGeoApiFlaskExtension()
    >>> pygeoapi_extension.init_app(app)

    After this, the flask app will have an instance of pygeoapi.core.Api in
    `app.extensions["pygeoapi"]` and there will be a blueprint with
    the pygeoapi-related views.
    """
    url_resolver: Callable

    def init_app(
            self,
            flask_app: flask.Flask,
            url_resolver: Callable,
    ):
        self.url_resolver = url_resolver
        api = core.Api(Path(flask_app.config["PYGEOAPI_OGC_API_SCHEMAS_BASE_DIR"]))
        flask_app.extensions["pygeoapi"] = {
            "api": api,
            "url_resolver": url_resolver,
        }
        flask_app.register_blueprint(
            pygeoapi_blueprint,
            url_prefix=flask_app.config["PYGEOAPI_ROUTE_PREFIX"]
        )


def create_app():
    """Create flask application."""

    app = flask.Flask(__name__)
    logging.basicConfig(level=logging.DEBUG if app.debug else logging.WARNING)
    # for brevity, a simple way to pass configuration to flask application
    app.config.update({
        "PYGEOAPI_OGC_API_SCHEMAS_BASE_DIR": Path(__file__).parent / "OGC/SCHEMAS_OPENGIS_NET/ogcapi",
        "PYGEOAPI_LIMIT": 100,
        "PYGEOAPI_VALIDATE_RESPONSES": True,
        "PYGEOAPI_ROUTE_PREFIX": "/pygeoapi",
    })
    app.config.from_prefixed_env()
    pygeoapi_extension = PyGeoApiFlaskExtension()
    pygeoapi_extension.init_app(app, url_resolver=flask_pygeoapi_url_resolver)
    return app
