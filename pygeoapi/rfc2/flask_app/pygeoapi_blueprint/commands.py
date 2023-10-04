"""CLI commands for pygeoapi's flask integration."""

from typing import Callable

import click
import json
import flask

from ... import core
from . import blueprint


@blueprint.cli.command("landing-page")
def landing_page():
    api: core.Api = flask.current_app.extensions["pygeoapi"]["api"]
    url_resolver: Callable = flask.current_app.extensions["pygeoapi"]["url_resolver"]
    response = api.get_landing_page(url_resolver=url_resolver)
    if flask.current_app.config["PYGEOAPI_VALIDATE_RESPONSES"]:
        api.validate(response)
    click.echo(json.dumps(response.as_dict(), indent=4))


@blueprint.cli.command("list-processes")
@click.option("--limit")
def list_processes(limit: int):
    api: core.Api = flask.current_app.extensions["pygeoapi"]["api"]
    response = api.list_processes(limit)
    if flask.current_app.config["PYGEOAPI_VALIDATE_RESPONSES"]:
        api.validate(response)
    click.echo(json.dumps(response.as_dict(), indent=4))
