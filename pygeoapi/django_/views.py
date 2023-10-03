# =================================================================
#
# Authors: Francesco Bartoli <francesco.bartoli@geobeyond.it>
#          Luca Delucchi <lucadeluge@gmail.com>
#          Krishna Lodha <krishnaglodha@gmail.com>
#          Tom Kralidis <tomkralidis@gmail.com>
#          Ricardo Garcia Silva <ricardo.garcia.silva@geobeyond.it>
#
# Copyright (c) 2022 Francesco Bartoli
# Copyright (c) 2022 Luca Delucchi
# Copyright (c) 2022 Krishna Lodha
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

"""Integration module for Django"""
from functools import wraps
from typing import Tuple, Dict, Optional

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from pygeoapi.api import API, APIRequest
from pygeoapi.openapi import get_oas


def adapt_django_request_to_pygeoapi(func):
    """Decorator that adapts django requests and generates responses.

    :param func: decorated function

    :returns: `func`

    This function must be used as a decorator on all django views. It
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

    api_ = API(settings.PYGEOAPI_CONFIG)

    @wraps(func)
    def wrapper(request: HttpRequest, *args, **kwargs):
        pygeoapi_request = APIRequest.with_data(
            request, getattr(api_, 'locales', set()))
        pygeoapi_response = func(pygeoapi_request, *args, **kwargs)
        headers, status, content = pygeoapi_response

        response = HttpResponse(content, status=status)
        for key, value in headers.items():
            response[key] = value
        return response

    return wrapper


@adapt_django_request_to_pygeoapi
def landing_page(pygeoapi_request: APIRequest) -> Tuple[Dict, int, str]:
    """
    OGC API landing page endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance

    :returns: Django HTTP Response
    """

    return _feed_response(pygeoapi_request, 'landing_page')


@adapt_django_request_to_pygeoapi
def openapi(pygeoapi_request: APIRequest) -> Tuple[Dict, int, str]:
    """
    OpenAPI endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance

    :returns: Django HTTP Response
    """

    openapi_config = get_oas(settings.PYGEOAPI_CONFIG)
    return _feed_response(pygeoapi_request, 'openapi', openapi_config)


@adapt_django_request_to_pygeoapi
def conformance(pygeoapi_request: APIRequest) -> Tuple[Dict, int, str]:
    """
    OGC API conformance endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance

    :returns: Django HTTP Response
    """

    return _feed_response(pygeoapi_request, 'conformance')


@adapt_django_request_to_pygeoapi
def collections(
        pygeoapi_request: APIRequest, collection_id: Optional[str] = None
) -> Tuple[Dict, int, str]:
    """
    OGC API collections endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier

    :returns: Django HTTP Response
    """

    return _feed_response(
        pygeoapi_request, 'describe_collections', collection_id)


@adapt_django_request_to_pygeoapi
def collection_queryables(
        pygeoapi_request: APIRequest,
        collection_id: Optional[str] = None
) -> Tuple[Dict, int, str]:
    """
    OGC API collections queryables endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier

    :returns: Django HTTP Response
    """

    return _feed_response(
        pygeoapi_request, 'get_collection_queryables', collection_id)


@adapt_django_request_to_pygeoapi
def collection_items(
        pygeoapi_request: APIRequest,
        collection_id: str
) -> Tuple[Dict, int, str]:
    """
    OGC API collections items endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier

    :returns: Django HTTP response
    """

    pygeoapi_response = None
    if pygeoapi_request.method == 'GET':
        pygeoapi_response = _feed_response(
            pygeoapi_request, 'get_collection_items', collection_id)
    elif pygeoapi_request.method == 'POST':
        content_type = pygeoapi_request.headers.get('Content-Type')
        if content_type is not None:
            if content_type == 'application/geo+json':
                pygeoapi_response = _feed_response(
                    pygeoapi_request, 'manage_collection_item',
                    'create', collection_id
                )
            else:
                pygeoapi_response = _feed_response(
                    pygeoapi_request, 'post_collection_items', collection_id)
    elif pygeoapi_request.method == 'OPTIONS':
        pygeoapi_response = _feed_response(
            pygeoapi_request, 'manage_collection_item',
            'options', collection_id
        )
    return pygeoapi_response


@adapt_django_request_to_pygeoapi
def collection_map(pygeoapi_request: APIRequest, collection_id: str):
    """
    OGC API - Maps map render endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier

    :returns: HTTP response
    """

    return _feed_response(
        pygeoapi_request, 'get_collection_map', collection_id)


@adapt_django_request_to_pygeoapi
def collection_style_map(
        pygeoapi_request: APIRequest,
        collection_id: str,
        style_id: str = None
):
    """
    OGC API - Maps map render endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier
    :param collection_id: style identifier

    :returns: HTTP response
    """

    return _feed_response(
        pygeoapi_request, 'get_collection_map', collection_id, style_id)


@adapt_django_request_to_pygeoapi
def collection_item(pygeoapi_request: APIRequest,
                    collection_id: str, item_id: str) -> Tuple[Dict, int, str]:
    """
    OGC API collections items endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier
    :param item_id: item identifier

    :returns: Django HTTP response
    """

    pygeoapi_response = None
    if pygeoapi_request.method == 'GET':
        pygeoapi_response = _feed_response(
            pygeoapi_request, 'get_collection_item', collection_id, item_id
        )
    elif pygeoapi_request.method == 'PUT':
        pygeoapi_response = _feed_response(
            pygeoapi_request, 'manage_collection_item', 'update',
            collection_id, item_id
        )
    elif pygeoapi_request.method == 'DELETE':
        pygeoapi_response = _feed_response(
            pygeoapi_request, 'manage_collection_item', 'delete',
            collection_id, item_id
        )
    elif pygeoapi_request.method == 'OPTIONS':
        pygeoapi_response = _feed_response(
            pygeoapi_request, 'manage_collection_item', 'options',
            collection_id, item_id)
    return pygeoapi_response


@adapt_django_request_to_pygeoapi
def collection_coverage(pygeoapi_request: APIRequest,
                        collection_id: str) -> Tuple[Dict, int, str]:
    """
    OGC API - Coverages coverage endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier

    :returns: Django HTTP response
    """

    return _feed_response(
        pygeoapi_request, 'get_collection_coverage', collection_id)


@adapt_django_request_to_pygeoapi
def collection_coverage_domainset(pygeoapi_request: APIRequest,
                                  collection_id: str) -> Tuple[Dict, int, str]:
    """
    OGC API - Coverages coverage domainset endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier

    :returns: Django HTTP response
    """

    return _feed_response(
        pygeoapi_request, 'get_collection_coverage_domainset', collection_id)


@adapt_django_request_to_pygeoapi
def collection_coverage_rangetype(pygeoapi_request: APIRequest,
                                  collection_id: str) -> Tuple[Dict, int, str]:
    """
    OGC API - Coverages coverage rangetype endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier

    :returns: Django HTTP response
    """

    return _feed_response(
        pygeoapi_request, 'get_collection_coverage_rangetype', collection_id)


@adapt_django_request_to_pygeoapi
def collection_tiles(
        pygeoapi_request: APIRequest,
        collection_id: str
) -> Tuple[Dict, int, str]:
    """
    OGC API - Tiles collection tiles endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier

    :returns: Django HTTP response
    """

    return _feed_response(
        pygeoapi_request, 'get_collection_tiles', collection_id)


@adapt_django_request_to_pygeoapi
def collection_tiles_metadata(
        pygeoapi_request: APIRequest,
        collection_id: str,
        tileMatrixSetId: str
) -> Tuple[Dict, int, str]:
    """
    OGC API - Tiles collection tiles metadata endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier
    :param tileMatrixSetId: identifier of tile matrix set

    :returns: Django HTTP response
    """

    return _feed_response(
        pygeoapi_request,
        'get_collection_tiles_metadata',
        collection_id,
        tileMatrixSetId,
    )


@adapt_django_request_to_pygeoapi
def collection_item_tiles(
        pygeoapi_request: APIRequest,
        collection_id: str,
        tileMatrixSetId: str,
        tileMatrix: str,
        tileRow: str,
        tileCol: str
) -> Tuple[Dict, int, str]:
    """
    OGC API - Tiles collection tiles data endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param collection_id: collection identifier
    :param tileMatrixSetId: identifier of tile matrix set
    :param tileMatrix: identifier of {z} matrix index
    :param tileRow: identifier of {y} matrix index
    :param tileCol: identifier of {x} matrix index

    :returns: Django HTTP response
    """

    return _feed_response(
        pygeoapi_request,
        'get_collection_tiles_metadata',
        collection_id,
        tileMatrixSetId,
        tileMatrix,
        tileRow,
        tileCol,
    )


@adapt_django_request_to_pygeoapi
def processes(pygeoapi_request: APIRequest,
              process_id: Optional[str] = None) -> Tuple[Dict, int, str]:
    """
    OGC API - Processes description endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param process_id: process identifier

    :returns: Django HTTP response
    """

    return _feed_response(pygeoapi_request, 'describe_processes', process_id)


@adapt_django_request_to_pygeoapi
def jobs(
        pygeoapi_request: APIRequest,
        job_id: Optional[str] = None
) -> Tuple[Dict, int, str]:
    """
    OGC API - Jobs endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param process_id: process identifier
    :param job_id: job identifier

    :returns: Django HTTP response
    """

    return _feed_response(pygeoapi_request, 'get_jobs', job_id)


@adapt_django_request_to_pygeoapi
def job_results(pygeoapi_request: APIRequest,
                job_id: Optional[str] = None) -> Tuple[Dict, int, str]:
    """
    OGC API - Job result endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param job_id: job identifier

    :returns: Django HTTP response
    """

    return _feed_response(pygeoapi_request, 'get_job_result', job_id)


@adapt_django_request_to_pygeoapi
def job_results_resource(
        pygeoapi_request: APIRequest,
        process_id: str,
        job_id: str,
        resource: str
) -> Tuple[Dict, int, str]:
    """
    OGC API - Job result resource endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param job_id: job identifier
    :param resource: job resource

    :returns: Django HTTP response
    """

    return _feed_response(
        pygeoapi_request,
        'get_job_result_resource',
        job_id,
        resource
    )


@adapt_django_request_to_pygeoapi
def get_collection_edr_query(pygeoapi_request: APIRequest, collection_id: str,
                             instance_id: str) -> Tuple[Dict, int, str]:
    """
    OGC API - EDR endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param job_id: job identifier
    :param resource: job resource

    :returns: Django HTTP response
    """

    query_type = pygeoapi_request.path_info.split('/')[-1]
    return _feed_response(
        pygeoapi_request,
        'get_collection_edr_query',
        collection_id,
        instance_id,
        query_type
    )


@adapt_django_request_to_pygeoapi
def stac_catalog_root(pygeoapi_request: APIRequest) -> Tuple[Dict, int, str]:
    """
    STAC root endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance

    :returns: Django HTTP response
    """

    return _feed_response(pygeoapi_request, 'get_stac_root')


@adapt_django_request_to_pygeoapi
def stac_catalog_path(
        pygeoapi_request: APIRequest, path: str) -> Tuple[Dict, int, str]:
    """
    STAC path endpoint

    :param pygeoapi_request: pygeoapi's APIRequest instance
    :param path: path

    :returns: Django HTTP response
    """

    return _feed_response(pygeoapi_request, 'get_stac_path', path)


def stac_catalog_search(request: HttpRequest) -> Tuple[Dict, int, str]:
    pass


def _feed_response(pygeoapi_request: APIRequest, api_definition: str,
                   *args, **kwargs) -> Tuple[Dict, int, str]:
    """Use pygeoapi api to process the input request"""

    api_ = API(settings.PYGEOAPI_CONFIG)
    api = getattr(api_, api_definition)
    return api(pygeoapi_request, *args, **kwargs)
