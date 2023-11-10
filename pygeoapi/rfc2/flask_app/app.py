"""Pygeoapi Flask integration.

This module defines two flask-related objects:

- PyGeoApiFlaskExtension - a Flask extension that can be used in order to
  provide pygeoapi functionality to a (potentially third-party) Flask
  application

- app - pygeoapi's official Flask application, which is created using the
  recommended factory pattern


Run pygeoapi dev web server like this:

FLASK_APP="pygeoapi.rfc2.flask_app.app" \
FLASK_DEBUG=true \
FLASK_SERVER_NAME=localhost:5000 \
FLASK_PYGEOAPI__METADATA__IDENTIFICATION__TITLE="some title" \
FLASK_PYGEOAPI__OGC_API_SCHEMAS_BASE_DIR=<schemas_base_dir> \
flask run

Run the CLI like this:

FLASK_APP="pygeoapi.rfc2.flask_app.app" \
FLASK_DEBUG=true \
FLASK_SERVER_NAME=localhost:5000 \
FLASK_PYGEOAPI__METADATA__IDENTIFICATION__TITLE="some title" \
FLASK_PYGEOAPI__OGC_API_SCHEMAS_BASE_DIR=<schemas_base_dir> \
flask pygeoapi --help

"""
import dataclasses
import logging
from typing import Callable

import flask
from flask_babel import (
    get_locale,
    Babel as FlaskBabelExtension,
)
from flask_openapi import OpenAPI as FlaskOpenApiExtension

from .. import (
    config as pygeoapi_config,
    core,
)

from .blueprints.pygeoapi import blueprint as pygeoapi_blueprint
from .blueprints.pygeoapi import (
    commands,
    views,
)

LOGGER = logging.getLogger(__name__)


def flask_babel_locale_selector():
    return flask.request.accept_languages.best_match(["en"])


def flask_pygeoapi_url_resolver(pygeoapi_method, *args, **kwargs):
    """A URL resolver for pygeoapi."""
    api: core.Api = flask.current_app.extensions["pygeoapi"]["api"]
    route_mapping = {
        api.get_landing_page: "pygeoapi.get_landing_page",
        api.list_processes: "pygeoapi.list_processes",
        api.get_conformance: "pygeoapi.get_conformance",
    }
    return flask.url_for(route_mapping[pygeoapi_method], _external=True)


class PyGeoApiFlaskExtension:
    """Flask extension for pygeoapi.

    Can be used on any flask application by doing:

    >>> app = create_app()  # or whatever way you create your flask app
    >>> pygeoapi_extension = PyGeoApiFlaskExtension()
    >>> pygeoapi_extension.init_app(app, url_resolver)

    After this, the flask app will have an instance of pygeoapi.core.Api in
    `app.extensions["pygeoapi"]` and there will be a blueprint with
    the pygeoapi-related views.

    ## Configuration

    This flask extension expects to get its configuration from flask by looking
    at the `PYGEOAPI` configuration key, which should be a mapping. The
    accepted config values map to the corresponding properties of
    `pygeoapi.config.PyGeoApiConfig`.

    """
    url_resolver: Callable

    def init_app(
            self,
            flask_app: flask.Flask,
            url_resolver: Callable,
    ):
        self.url_resolver = url_resolver
        conf = self._get_pygeoapi_config(flask_app)
        api = core.get_api(self._get_pygeoapi_config(flask_app))
        flask_app.extensions["pygeoapi"] = {
            "api": api,
            "url_resolver": url_resolver,
        }
        flask_app.config["PYGEOAPI"] = dataclasses.asdict(conf)
        flask_app.register_blueprint(
            pygeoapi_blueprint,
            url_prefix=flask_app.config.get(
                "PYGEOAPI", {}).get("ROUTE_PREFIX", "/pygeoapi")
        )

    def _get_pygeoapi_config(self, flask_app: flask.Flask):
        config = pygeoapi_config.get_config()
        config.debug = flask_app.debug
        provided_by_flask = flask_app.config.get("PYGEOAPI", {})
        if schemas_dir := provided_by_flask.get("OGC_API_SCHEMAS_BASE_DIR"):
            config.ogc_api_schemas_base_dir = schemas_dir
        if (limit := provided_by_flask.get("PAGINATION_LIMIT")) is not None:
            config.pagination_limit = int(limit)
        if (validate := provided_by_flask.get("VALIDATE_RESPONSES")) is not None:
            truthy_strings = (
                "yes",
                "true",
                "1",
            )
            config.validate_responses = (
                True if validate.lower() in truthy_strings else False)
        metadata_sections = (
            "identification",
            "license",
            "provider",
            "point_of_contact",
        )
        for metadata_section in metadata_sections:
            config_object = getattr(config.metadata, metadata_section)
            provided_section = provided_by_flask.get(
                "METADATA", {}).get(metadata_section.upper(), {})
            for key, value in provided_section.items():
                setattr(config_object, key.lower(), value)
        return config


def create_app():
    """Create flask application."""

    app = flask.Flask(__name__)
    app.config.from_prefixed_env()
    logging.basicConfig(level=logging.DEBUG if app.debug else logging.WARNING)
    FlaskBabelExtension(app=app, locale_selector=flask_babel_locale_selector)
    app.jinja_env.globals["get_locale"] = get_locale
    FlaskOpenApiExtension(app=app)
    pygeoapi_extension = PyGeoApiFlaskExtension()
    pygeoapi_extension.init_app(app, url_resolver=flask_pygeoapi_url_resolver)
    return app
