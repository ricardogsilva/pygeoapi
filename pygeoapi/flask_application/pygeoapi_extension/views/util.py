from typing import (
    Callable,
    Union,
)

import flask
from flask import (
    make_response,
    Request,
    Response,
)

from pygeoapi.api import (
    API,
    APIRequest,
    apply_gzip,
)


def execute_from_flask(
        api_instance: API,
        api_function: Callable,
        request: Request,
        *args,
        skip_valid_check=False,
        alternative_api=None
) -> Response:
    """
    Executes API function from Flask

    :param api_function: API function
    :param request: request object
    :param *args: variable length additional arguments
    :param skip_validity_check: bool
    :param alternative_api: specify custom api instance such as Admin

    :returns: A Response instance
    """

    api_request = APIRequest.from_flask(request, api_instance.locales)

    content: Union[str, bytes]

    if not skip_valid_check and not api_request.is_valid():
        headers, status, content = api_instance.get_format_exception(api_request)
    else:
        headers, status, content = api_function(api_instance, api_request, *args)
        content = apply_gzip(headers, content)

    response = make_response(content, status)

    if headers:
        response.headers = headers
    return response
