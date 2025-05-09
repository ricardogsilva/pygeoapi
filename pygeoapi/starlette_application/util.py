import asyncio
from typing import (
    Callable,
    Union
)

from starlette.requests import Request
from starlette.responses import (
    HTMLResponse,
    JSONResponse,
    Response,
)

from pygeoapi.api import (
    API,
    APIRequest,
    apply_gzip,
)


async def execute_from_starlette(
        api_instance: API,
        api_function: Callable,
        request: Request,
        *args,
        skip_valid_check=False,
) -> Response:
    api_request = await APIRequest.from_starlette(request, api_instance.locales)
    content: Union[str, bytes]
    if not skip_valid_check and not api_request.is_valid():
        headers, status, content = api_instance.get_format_exception(api_request)
    else:

        loop = asyncio.get_running_loop()
        headers, status, content = await loop.run_in_executor(
            None, call_api_threadsafe, loop, api_function,
            api_instance, api_request, *args)
        # NOTE: that gzip currently doesn't work in starlette
        #       https://github.com/geopython/pygeoapi/issues/1591
        content = apply_gzip(headers, content)

    response = _to_response(headers, status, content)

    return response


def call_api_threadsafe(
        loop: asyncio.AbstractEventLoop, api_call: Callable, *args
) -> tuple:
    """
    The api call needs a running loop. This method is meant to be called
    from a thread that has no loop running.

    :param loop: The loop to use.
    :param api_call: The API method to call.
    :param args: Arguments to pass to the API method.
    :returns: The api call result tuple.
    """
    asyncio.set_event_loop(loop)
    return api_call(*args)


def _to_response(headers, status, content):
    if headers['Content-Type'] == 'text/html':
        response = HTMLResponse(content=content, status_code=status)
    else:
        if isinstance(content, dict):
            response = JSONResponse(content, status_code=status)
        else:
            response = Response(content, status_code=status)

    if headers is not None:
        response.headers.update(headers)
    return response
