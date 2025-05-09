from starlette.requests import Request
from starlette.routing import Route

import pygeoapi.admin
from pygeoapi.starlette_application.util import execute_from_starlette


async def admin_config(request: Request):
    """
    Admin endpoint

    :returns: Starlette HTTP Response
    """

    if request.method == 'GET':
        return await execute_from_starlette(
            request.app.state.PYGEOAPI.admin_api,
            pygeoapi.admin.get_config_,
            request
        )
    elif request.method == 'PUT':
        return await execute_from_starlette(
            request.app.state.PYGEOAPI.admin_api,
            pygeoapi.admin.put_config,
            request
        )
    elif request.method == 'PATCH':
        return await execute_from_starlette(
            request.app.state.PYGEOAPI.admin_api,
            pygeoapi.admin.patch_config,
            request
        )


async def admin_config_resources(request: Request):
    """
    Resources endpoint

    :returns: HTTP response
    """

    if request.method == 'GET':
        return await execute_from_starlette(
            request.app.state.PYGEOAPI.admin_api,
            pygeoapi.admin.get_resources,
            request
        )
    elif request.method == 'POST':
        return await execute_from_starlette(
            request.app.state.PYGEOAPI.admin_api,
            pygeoapi.admin.put_resource,
            request
        )


async def admin_config_resource(request: Request, resource_id: str):
    """
    Resource endpoint

    :param resource_id: resource identifier

    :returns: Starlette HTTP Response
    """

    if 'resource_id' in request.path_params:
        resource_id = request.path_params['resource_id']

    if request.method == 'GET':
        return await execute_from_starlette(
            request.app.state.PYGEOAPI.admin_api,
            pygeoapi.admin.get_resource,
            request,
            resource_id
        )
    elif request.method == 'PUT':
        return await execute_from_starlette(
            request.app.state.PYGEOAPI.admin_api,
            pygeoapi.admin.put_resource,
            request,
            resource_id
        )
    elif request.method == 'PATCH':
        return await execute_from_starlette(
            request.app.state.PYGEOAPI.admin_api,
            pygeoapi.admin.patch_resource,
            request,
            resource_id
        )
    elif request.method == 'DELETE':
        return await execute_from_starlette(
            request.app.state.PYGEOAPI.admin_api,
            pygeoapi.admin.delete_resource,
            request,
            resource_id
        )


routes = [
    Route('/config', admin_config, methods=['GET', 'PUT', 'PATCH']),
    Route('/config/resources', admin_config_resources, methods=['GET', 'POST']),  # noqa
    Route('/config/resources/{resource_id:path}', admin_config_resource,
          methods=['GET', 'PUT', 'PATCH', 'DELETE'])
]