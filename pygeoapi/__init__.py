# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#          Ricardo Garcia Silva <ricardo.garcia.silva@geobeyond.it>
#
# Copyright (c) 2021 Tom Kralidis
# Copyright (c) 2023 Ricardo Garcia Silva
# Copyright (c) 2025 Angelos Tzotsos
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

__version__ = '0.21.dev0'

import os
from pathlib import Path

import click
try:
    # importlib.metadata is part of Python's standard library from 3.8
    from importlib.metadata import entry_points
except ImportError:
    from importlib_metadata import entry_points

import uvicorn

from pygeoapi import flask_application
from pygeoapi.api import API
from pygeoapi.conf import PygeoapiConfiguration
from pygeoapi.openapi import get_oas
from pygeoapi.config import (
    config,
    get_config,
)
from pygeoapi.openapi import (
    load_openapi_document,
    openapi,
)



def _find_plugins():
    """
    A decorator to find pygeoapi CLI plugins provided by third-party packages.

    pygeoapi plugins can hook into the pygeoapi CLI by providing their CLI
    functions and then using an entry_point named 'pygeoapi'.
    """

    def decorator(click_group):
        try:
            found_entrypoints = entry_points(group="pygeoapi")
        except TypeError:
            # earlier versions of importlib_metadata did not have the
            # `group` kwarg. More detail:
            #
            # https://github.com/geopython/pygeoapi/issues/1241#issuecomment-1536128897  # noqa: E501
            for group, entries in entry_points().items():
                if group == "pygeoapi":
                    found_entrypoints = entries
                    break
            else:
                found_entrypoints = []
        for entry_point in found_entrypoints:
            try:
                click_group.add_command(entry_point.load())
            except Exception as err:
                print(err)
        return click_group

    return decorator


@click.group()
@click.version_option(version=__version__)
def cli():
    pass


@_find_plugins()
@cli.group()
def plugins():
    """Additional commands provided by third-party pygeoapi plugins"""
    pass


@cli.command()
@click.option('--flask', 'server', flag_value="flask", default=True)
@click.option('--starlette', 'server', flag_value="starlette")
@click.option('--django', 'server', flag_value="django")
@click.option('--starlette-application', 'server', flag_value="starlette_application")
@click.pass_context
def serve(ctx, server):
    """Run the server with different daemon type (--flask is the default)"""
    if (config_path:=os.getenv('PYGEOAPI_CONFIG')) is not None:
        pygeoapi_config = PygeoapiConfiguration.from_configuration_file(config_path)
        print("Initialized pygeoapi config")
        openapi_document = get_oas(pygeoapi_config)
        print("Generated OpenAPI document")
        pygeoapi_api = API(pygeoapi_config, openapi_document)
        print("Initialized pygeoapi API")
        if server == 'flask':
            app = flask_application.get_app_from_pygeoapi_api(pygeoapi_api)
            app.run(
                debug=True,
                host=app.extensions['pygeoapi']['api'].config['server']['bind']['host'],
                port=app.extensions['pygeoapi']['api'].config['server']['bind']['port']
            )
        elif server == "starlette":
            from pygeoapi.starlette_app import serve as serve_starlette
            ctx.invoke(serve_starlette)
        elif server == "starlette_application":
            log_level = 'info'
            if pygeoapi_api.config['server'].get('debug', False):
                log_level = 'debug'
            uvicorn.run(
                "pygeoapi.starlette_application:get_app",
                reload=True,
                log_level=log_level,
                loop='asyncio',
                host=pygeoapi_api.config['server']['bind']['host'],
                port=pygeoapi_api.config['server']['bind']['port'])
        elif server == "django":
            from pygeoapi.django_app import main as serve_django
            ctx.invoke(serve_django)
        else:
            raise click.ClickException('--flask/--starlette/--django is required')
    else:
        raise RuntimeError('PYGEOAPI_CONFIG environment variable not set')



cli.add_command(config)
cli.add_command(openapi)