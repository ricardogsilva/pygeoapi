# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#          Ricardo Garcia Silva <ricardo.garcia.silva@gmail.com>
#
# Copyright (c) 2018 Tom Kralidis
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

import typing

import click
from importlib_metadata import version
from pygeoapi.openapi import generate_openapi_document


cli = click.Group()
cli.version = version('pygeoapi')


FLASK_CHOICE = 'flask'
STARLETTE_CHOICE = 'starlette'
FRAMEWORK_CHOICES = (
    FLASK_CHOICE,
    STARLETTE_CHOICE,
)

@cli.command()
@click.argument(
    'server', type=click.Choice(FRAMEWORK_CHOICES), default=FLASK_CHOICE)
@click.option('--debug', '-d', default=False, is_flag = True, help='debug')
def serve(server: str, debug: bool):
    """Run a development server"""

    if server == FLASK_CHOICE:
        serve_flask()
    elif server == STARLETTE_CHOICE:
        serve_starlette()
    else:
        raise click.ClickException('--flask/--starlette is required')


cli.add_command(generate_openapi_document)


def serve_flask(debug: typing.Optional[bool] = False):
    """ Serve pygeoapi via Flask.

    Not recommend for production.

    """

    from pygeoapi.flask_app import APP, api_
    APP.run(
        debug=debug,
        host=api_.config['server']['bind']['host'],
        port=api_.config['server']['bind']['port']
    )


def serve_starlette(debug: typing.Optional[bool] = False):
    """Serve pygeoapi via Starlette.

    Runs pygeoapi as a uvicorn server. Not recommend for production.

    """

    import uvicorn
    from pygeoapi.starlette_app import app, api_

    #    setup_logger(CONFIG['logging'])
    uvicorn.run(
        app,
        debug=debug,
        host=api_.config['server']['bind']['host'],
        port=api_.config['server']['bind']['port']
    )
