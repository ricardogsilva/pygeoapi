# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#          Norman Barker <norman.barker@gmail.com>
#          Ricardo Garcia Silva <ricardo.garcia.silva@geobeyond.it>
#
# Copyright (c) 2022 Tom Kralidis
# Copyright (c) 2023 Ricardo Garcia Silva
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

"""Flask module providing the route paths to the api"""

from functools import wraps
import os

import click

from flask import Flask, Blueprint, make_response, request, send_from_directory

from pygeoapi.api import API
from pygeoapi.request import APIRequest
from pygeoapi.util import get_mimetype, yaml_load, get_api_rules


def adapt_flask_request_to_pygeoapi(func):
    """Decorator that adapts Flask requests and generates responses.

    :param func: decorated function

    :returns: `func`

    This function must be used as a decorator on all flask routes. It
    performs the following steps:

    1. Transforms incoming flask Request instance into an :class:
       `APIRequest` instance;
    2. Proceeds to execute whatever code is defined in the decorated function
    3. Uses the generated response, which is expected to be a standard
       pygeoapi API response (consisting of a three-element tuple of a
       dictionary with response headers, an integer with the HTTP status code
       and the response body content) to generate a suitable flask Response
       instance
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        pygeoapi_request = APIRequest.with_data(
            request, getattr(api_, 'locales', set()))
        pygeoapi_response = func(pygeoapi_request, *args, **kwargs)
        headers, status, content = pygeoapi_response
        response = make_response(content, status)
        if headers:
            response.headers = headers
        return response

    return wrapper


if 'PYGEOAPI_CONFIG' not in os.environ:
    raise RuntimeError('PYGEOAPI_CONFIG environment variable not set')

with open(os.environ.get('PYGEOAPI_CONFIG'), encoding='utf8') as fh:
    CONFIG = yaml_load(fh)

API_RULES = get_api_rules(CONFIG)

STATIC_FOLDER = 'static'
if 'templates' in CONFIG['server']:
    STATIC_FOLDER = CONFIG['server']['templates'].get('static', 'static')

APP = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='/static')
APP.url_map.strict_slashes = API_RULES.strict_slashes

BLUEPRINT = Blueprint(
    'pygeoapi',
    __name__,
    static_folder=STATIC_FOLDER,
    url_prefix=API_RULES.get_url_prefix('flask')
)

# CORS: optionally enable from config.
if CONFIG['server'].get('cors', False):
    try:
        from flask_cors import CORS
        CORS(APP)
    except ModuleNotFoundError:
        print('Python package flask-cors required for CORS support')

APP.config['JSONIFY_PRETTYPRINT_REGULAR'] = CONFIG['server'].get(
    'pretty_print', True)

api_ = API(CONFIG)

OGC_SCHEMAS_LOCATION = CONFIG['server'].get('ogc_schemas_location')

if (OGC_SCHEMAS_LOCATION is not None and
        not OGC_SCHEMAS_LOCATION.startswith('http')):
    # serve the OGC schemas locally

    if not os.path.exists(OGC_SCHEMAS_LOCATION):
        raise RuntimeError('OGC schemas misconfigured')

    @BLUEPRINT.route('/schemas/<path:path>', methods=['GET'])
    def schemas(path):
        """
        Serve OGC schemas locally

        :param path: path of the OGC schema document

        :returns: HTTP response
        """

        full_filepath = os.path.join(OGC_SCHEMAS_LOCATION, path)
        dirname_ = os.path.dirname(full_filepath)
        basename_ = os.path.basename(full_filepath)

        # TODO: better sanitization?
        path_ = dirname_.replace('..', '').replace('//', '')
        return send_from_directory(path_, basename_,
                                   mimetype=get_mimetype(basename_))


@BLUEPRINT.route('/')
@adapt_flask_request_to_pygeoapi
def landing_page(pygeoapi_request: APIRequest):
    """
    OGC API landing page endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance

    :returns: HTTP response
    """
    return api_.landing_page(pygeoapi_request)


@BLUEPRINT.route('/openapi')
@adapt_flask_request_to_pygeoapi
def openapi(pygeoapi_request: APIRequest):
    """
    OpenAPI endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :returns: HTTP response
    """
    with open(os.environ.get('PYGEOAPI_OPENAPI'), encoding='utf8') as ff:
        if os.environ.get('PYGEOAPI_OPENAPI').endswith(('.yaml', '.yml')):
            openapi_ = yaml_load(ff)
        else:  # JSON string, do not transform
            openapi_ = ff.read()
    return api_.openapi(pygeoapi_request, openapi_)


@BLUEPRINT.route('/conformance')
@adapt_flask_request_to_pygeoapi
def conformance(pygeoapi_request: APIRequest):
    """
    OGC API conformance endpoint

    :returns: HTTP response
    """
    return api_.conformance(pygeoapi_request)


@BLUEPRINT.route('/collections')
@BLUEPRINT.route('/collections/<path:collection_id>')
@adapt_flask_request_to_pygeoapi
def collections(pygeoapi_request: APIRequest, collection_id=None):
    """
    OGC API collections endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier

    :returns: HTTP response
    """
    return api_.describe_collections(pygeoapi_request, collection_id)


@BLUEPRINT.route('/collections/<path:collection_id>/queryables')
@adapt_flask_request_to_pygeoapi
def collection_queryables(pygeoapi_request: APIRequest, collection_id=None):
    """
    OGC API collections querybles endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier

    :returns: HTTP response
    """
    return api_.get_collection_queryables(pygeoapi_request, collection_id)


@BLUEPRINT.route('/collections/<path:collection_id>/items',
                 methods=['GET', 'POST', 'OPTIONS'],
                 provide_automatic_options=False)
@BLUEPRINT.route('/collections/<path:collection_id>/items/<path:item_id>',
                 methods=['GET', 'PUT', 'DELETE', 'OPTIONS'],
                 provide_automatic_options=False)
@adapt_flask_request_to_pygeoapi
def collection_items(
        pygeoapi_request: APIRequest, collection_id, item_id=None):
    """
    OGC API collections items endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier
    :param item_id: item identifier

    :returns: HTTP response
    """

    pygeoapi_response = None
    if item_id is None:
        if pygeoapi_request.method == 'GET':  # list items
            pygeoapi_response = api_.get_collection_items(
                pygeoapi_request, collection_id)
        elif pygeoapi_request.method == 'POST':  # filter or manage items
            content_type = pygeoapi_request.headers.get("Content-Type")
            if content_type is not None:
                if content_type == 'application/geo+json':
                    pygeoapi_response = api_.manage_collection_item(
                        pygeoapi_request, 'create', collection_id)
                else:
                    pygeoapi_response = api_.post_collection_items(
                        pygeoapi_request, collection_id)
        elif pygeoapi_request.method == 'OPTIONS':
            pygeoapi_response = api_.manage_collection_item(
                pygeoapi_request, 'options', collection_id)
    elif pygeoapi_request.method == 'DELETE':
        pygeoapi_response = api_.manage_collection_item(
            pygeoapi_request, 'delete', collection_id, item_id)
    elif pygeoapi_request.method == 'PUT':
        pygeoapi_response = api_.manage_collection_item(
            pygeoapi_request, 'update', collection_id, item_id)
    elif pygeoapi_request.method == 'OPTIONS':
        pygeoapi_response = api_.manage_collection_item(
            pygeoapi_request, 'options', collection_id, item_id)
    else:
        pygeoapi_response = api_.get_collection_item(
            pygeoapi_request, collection_id, item_id)
    return pygeoapi_response


@BLUEPRINT.route('/collections/<path:collection_id>/coverage')
@adapt_flask_request_to_pygeoapi
def collection_coverage(pygeoapi_request: APIRequest, collection_id):
    """
    OGC API - Coverages coverage endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier

    :returns: HTTP response
    """
    return api_.get_collection_coverage(pygeoapi_request, collection_id)


@BLUEPRINT.route('/collections/<path:collection_id>/coverage/domainset')
@adapt_flask_request_to_pygeoapi
def collection_coverage_domainset(pygeoapi_request: APIRequest, collection_id):
    """
    OGC API - Coverages coverage domainset endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier

    :returns: HTTP response
    """
    return api_.get_collection_coverage_domainset(
        pygeoapi_request, collection_id)


@BLUEPRINT.route('/collections/<path:collection_id>/coverage/rangetype')
@adapt_flask_request_to_pygeoapi
def collection_coverage_rangetype(pygeoapi_request: APIRequest, collection_id):
    """
    OGC API - Coverages coverage rangetype endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier

    :returns: HTTP response
    """
    return api_.get_collection_coverage_rangetype(
        pygeoapi_request, collection_id)


@BLUEPRINT.route('/collections/<path:collection_id>/tiles')
@adapt_flask_request_to_pygeoapi
def get_collection_tiles(pygeoapi_request: APIRequest, collection_id=None):
    """
    OGC open api collections tiles access point

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier

    :returns: HTTP response
    """
    return api_.get_collection_tiles(pygeoapi_request, collection_id)


@BLUEPRINT.route('/collections/<path:collection_id>/tiles/<tileMatrixSetId>')
@BLUEPRINT.route('/collections/<path:collection_id>/tiles/<tileMatrixSetId>/metadata')  # noqa
@adapt_flask_request_to_pygeoapi
def get_collection_tiles_metadata(
        pygeoapi_request: APIRequest,
        collection_id=None,
        tileMatrixSetId=None
):
    """
    OGC open api collection tiles service metadata

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier
    :param tileMatrixSetId: identifier of tile matrix set

    :returns: HTTP response
    """
    return api_.get_collection_tiles_metadata(
        pygeoapi_request, collection_id, tileMatrixSetId)


@BLUEPRINT.route('/collections/<path:collection_id>/tiles/\
<tileMatrixSetId>/<tileMatrix>/<tileRow>/<tileCol>')
@adapt_flask_request_to_pygeoapi
def get_collection_tiles_data(
        pygeoapi_request: APIRequest,
        collection_id=None,
        tileMatrixSetId=None,
        tileMatrix=None,
        tileRow=None,
        tileCol=None
):
    """
    OGC open api collection tiles service data

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier
    :param tileMatrixSetId: identifier of tile matrix set
    :param tileMatrix: identifier of {z} matrix index
    :param tileRow: identifier of {y} matrix index
    :param tileCol: identifier of {x} matrix index

    :returns: HTTP response
    """
    return api_.get_collection_tiles_data(
        pygeoapi_request, collection_id, tileMatrixSetId,
        tileMatrix, tileRow, tileCol
    )


@BLUEPRINT.route('/collections/<collection_id>/map')
@BLUEPRINT.route('/collections/<collection_id>/styles/<style_id>/map')
@adapt_flask_request_to_pygeoapi
def collection_map(pygeoapi_request: APIRequest, collection_id, style_id=None):
    """
    OGC API - Maps map render endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier
    :param style_id: style identifier

    :returns: HTTP response
    """

    return api_.get_collection_map(pygeoapi_request, collection_id, style_id)


@BLUEPRINT.route('/processes')
@BLUEPRINT.route('/processes/<process_id>')
@adapt_flask_request_to_pygeoapi
def get_processes(pygeoapi_request: APIRequest, process_id=None):
    """
    OGC API - Processes description endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param process_id: process identifier

    :returns: HTTP response
    """
    return api_.describe_processes(pygeoapi_request, process_id)


@BLUEPRINT.route('/jobs')
@BLUEPRINT.route('/jobs/<job_id>',
                 methods=['GET', 'DELETE'])
@adapt_flask_request_to_pygeoapi
def get_jobs(pygeoapi_request: APIRequest, job_id=None):
    """
    OGC API - Processes jobs endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param job_id: job identifier

    :returns: HTTP response
    """
    if job_id is None:
        pygeoapi_response = api_.get_jobs(pygeoapi_request)
    else:
        if pygeoapi_request.method == 'DELETE':  # dismiss job
            pygeoapi_response = api_.delete_job(pygeoapi_request, job_id)
        else:  # Return status of a specific job
            pygeoapi_response = api_.get_jobs(pygeoapi_request, job_id)
    return pygeoapi_response


@BLUEPRINT.route('/processes/<process_id>/execution', methods=['POST'])
@adapt_flask_request_to_pygeoapi
def execute_process_jobs(pygeoapi_request: APIRequest, process_id):
    """
    OGC API - Processes execution endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param process_id: process identifier

    :returns: HTTP response
    """
    return api_.execute_process(pygeoapi_request, process_id)


@BLUEPRINT.route('/jobs/<job_id>/results',
                 methods=['GET'])
@adapt_flask_request_to_pygeoapi
def get_job_result(pygeoapi_request: APIRequest, job_id=None):
    """
    OGC API - Processes job result endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param job_id: job identifier

    :returns: HTTP response
    """
    return api_.get_job_result(pygeoapi_request, job_id)


@BLUEPRINT.route('/collections/<path:collection_id>/position')
@BLUEPRINT.route('/collections/<path:collection_id>/area')
@BLUEPRINT.route('/collections/<path:collection_id>/cube')
@BLUEPRINT.route('/collections/<path:collection_id>/radius')
@BLUEPRINT.route('/collections/<path:collection_id>/trajectory')
@BLUEPRINT.route('/collections/<path:collection_id>/corridor')
@BLUEPRINT.route('/collections/<path:collection_id>/instances/<instance_id>/position')  # noqa
@BLUEPRINT.route('/collections/<path:collection_id>/instances/<instance_id>/area')  # noqa
@BLUEPRINT.route('/collections/<path:collection_id>/instances/<instance_id>/cube')  # noqa
@BLUEPRINT.route('/collections/<path:collection_id>/instances/<instance_id>/radius')  # noqa
@BLUEPRINT.route('/collections/<path:collection_id>/instances/<instance_id>/trajectory')  # noqa
@BLUEPRINT.route('/collections/<path:collection_id>/instances/<instance_id>/corridor')  # noqa
@adapt_flask_request_to_pygeoapi
def get_collection_edr_query(
        pygeoapi_request: APIRequest, collection_id, instance_id=None):
    """
    OGC EDR API endpoints

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier
    :param instance_id: instance identifier

    :returns: HTTP response
    """
    query_type = pygeoapi_request.path_info.split('/')[-1]
    return api_.get_collection_edr_query(
        pygeoapi_request, collection_id, instance_id, query_type)


@BLUEPRINT.route('/stac')
@adapt_flask_request_to_pygeoapi
def stac_catalog_root(pygeoapi_request: APIRequest):
    """
    STAC root endpoint

    :returns: HTTP response
    """
    return api_.get_stac_root(pygeoapi_request)


@BLUEPRINT.route('/stac/<path:path>')
@adapt_flask_request_to_pygeoapi
def stac_catalog_path(pygeoapi_request: APIRequest, path):
    """
    STAC path endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param path: path

    :returns: HTTP response
    """
    return api_.get_stac_path(pygeoapi_request, path)


APP.register_blueprint(BLUEPRINT)


@click.command()
@click.pass_context
@click.option('--debug', '-d', default=False, is_flag=True, help='debug')
def serve(ctx, server=None, debug=False):
    """
    Serve pygeoapi via Flask. Runs pygeoapi
    as a flask server. Not recommend for production.

    :param server: `string` of server type
    :param debug: `bool` of whether to run in debug mode

    :returns: void
    """

    # setup_logger(CONFIG['logging'])
    APP.run(debug=True, host=api_.config['server']['bind']['host'],
            port=api_.config['server']['bind']['port'])


if __name__ == '__main__':  # run locally, for testing
    serve()
