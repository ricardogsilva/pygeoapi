import logging

import flask
import jinja2

from ... import core
from . import blueprint

# blueprint = flask.Blueprint("pygeoapi", __name__)
LOGGER = logging.getLogger(__name__)


@blueprint.route("/")
def get_landing_page():
    api: core.Api = flask.current_app.extensions["pygeoapi"]["api"]
    api_response = api.get_landing_page(
        url_resolver=flask.current_app.extensions["pygeoapi"]["url_resolver"])
    LOGGER.debug(f"{api_response=}")
    if flask.current_app.config["PYGEOAPI_VALIDATE_RESPONSES"]:
        api.validate(api_response)
    if "html" in flask.request.headers["accept"]:
        landing_page_template = jinja2.Template(
            """
            <h1>{{ title }}</h1>
            <p>{{ description }}</p>
            {% if links|length > 0 %}
                <ul>
                {% for link in links %}
                <li><a href='{{ link.href }}'>{{ link.title }}</a></li>
                {% endfor %}
                </ul>
            {% else %}
                <p>This landing page has no links? It should fail validation then</p>
            {% endif %}
            """
        )
        return flask.render_template(landing_page_template, **api_response.as_dict())
    else:
        return api_response.as_dict()


@blueprint.route("/processes")
def list_processes():
    limit = int(
        flask.request.args.get(
            "limit", flask.current_app.config["PYGEOAPI_LIMIT"]
        )
    )
    api = flask.current_app.extensions["pygeoapi"]["api"]
    api_response = api.list_processes(limit)
    if flask.current_app.config["PYGEOAPI_VALIDATE_RESPONSES"]:
        api.validate(api_response)
    return api_response.as_dict()
