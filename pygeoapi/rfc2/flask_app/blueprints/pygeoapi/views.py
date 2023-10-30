import logging

import flask

from .... import core
from . import blueprint

LOGGER = logging.getLogger(__name__)


@blueprint.route("/")
def get_landing_page():
    api: core.Api = flask.current_app.extensions["pygeoapi"]["api"]
    url_resolver = flask.current_app.extensions["pygeoapi"]["url_resolver"]
    api_response = api.get_landing_page(url_resolver=url_resolver)
    if flask.current_app.config["PYGEOAPI"]["validate_responses"]:
        api.validate(api_response)
    if "html" in flask.request.headers["accept"]:
        return flask.render_template(
            "pygeoapi/landing-page.j2.html",
            data=api_response
        )
    else:
        return api_response.as_dict()


@blueprint.route("/conformance")
def get_conformance():
    api: core.Api = flask.current_app.extensions["pygeoapi"]["api"]
    api_response = api.get_conformance()
    # since this is an HTTP application with support for HTML, add the
    # additional conformance classes for HTML and OpenAPI 3.0
    api_response.conformsTo.extend(
        [
            "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/html",
            "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/oas30",
        ]
    )
    if flask.current_app.config["PYGEOAPI"]["validate_responses"]:
        api.validate(api_response)
    return api_response.as_dict()


@blueprint.route("/processes")
def list_processes():
    limit = int(
        flask.request.args.get(
            "limit", flask.current_app.config["PYGEOAPI"]["LIMIT"]
        )
    )
    api = flask.current_app.extensions["pygeoapi"]["api"]
    api_response = api.list_processes(limit)
    if flask.current_app.config["PYGEOAPI"]["validate_responses"]:
        api.validate(api_response)
    return api_response.as_dict()
