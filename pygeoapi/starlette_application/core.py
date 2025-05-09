from starlette.requests import Request
from starlette.routing import Route

import pygeoapi.api
import pygeoapi.api.coverages
import pygeoapi.api.environmental_data_retrieval
import pygeoapi.api.itemtypes
import pygeoapi.api.maps
import pygeoapi.api.processes
import pygeoapi.api.stac
import pygeoapi.api.tiles
from pygeoapi.starlette_application.util import execute_from_starlette


async def landing_page(request: Request):
    """
    OGC API landing page endpoint

    :param request: Starlette Request instance

    :returns: Starlette HTTP Response
    """
    return await execute_from_starlette(
        request.app.state.PYGEOAPI.api, pygeoapi.api.landing_page, request)


async def openapi(request: Request):
    """
    OpenAPI endpoint

    :param request: Starlette Request instance

    :returns: Starlette HTTP Response
    """
    return await execute_from_starlette(
        request.app.state.PYGEOAPI.api, pygeoapi.api.openapi_, request)


async def conformance(request: Request):
    """
    OGC API conformance endpoint

    :param request: Starlette Request instance

    :returns: Starlette HTTP Response
    """
    return await execute_from_starlette(
        request.app.state.PYGEOAPI.api, pygeoapi.api.conformance, request)


async def get_tilematrix_set(request: Request, tileMatrixSetId=None):
    """
    OGC API TileMatrixSet endpoint

    :param tileMatrixSetId: identifier of tile matrix set
    :returns: HTTP response
    """
    if 'tileMatrixSetId' in request.path_params:
        tileMatrixSetId = request.path_params['tileMatrixSetId']

    return await execute_from_starlette(
        request.app.state.PYGEOAPI.api, pygeoapi.api.tiles.tilematrixset,
        request, tileMatrixSetId,
    )


async def get_tilematrix_sets(request: Request):
    """
    OGC API TileMatrixSets endpoint

    :returns: HTTP response
    """
    return await execute_from_starlette(
        request.app.state.PYGEOAPI.api,
        pygeoapi.api.tiles.tilematrixsets,
        request
    )


async def collection_schema(request: Request, collection_id=None):
    """
    OGC API collections schema endpoint

    :param request: Starlette Request instance
    :param collection_id: collection identifier

    :returns: Starlette HTTP Response
    """
    if 'collection_id' in request.path_params:
        collection_id = request.path_params['collection_id']

    return await execute_from_starlette(
        request.app.state.PYGEOAPI.api,
        pygeoapi.api.get_collection_schema,
        request,
        collection_id
    )


async def collection_queryables(request: Request, collection_id=None):
    """
    OGC API collections queryables endpoint

    :param request: Starlette Request instance
    :param collection_id: collection identifier

    :returns: Starlette HTTP Response
    """
    if 'collection_id' in request.path_params:
        collection_id = request.path_params['collection_id']

    return await execute_from_starlette(
        request.app.state.PYGEOAPI.api,
        pygeoapi.api.itemtypes.get_collection_queryables,
        request,
        collection_id,
    )


async def get_collection_tiles(request: Request, collection_id=None):
    """
    OGC open api collections tiles access point

    :param request: Starlette Request instance
    :param collection_id: collection identifier

    :returns: Starlette HTTP Response
    """
    if 'collection_id' in request.path_params:
        collection_id = request.path_params['collection_id']

    return await execute_from_starlette(
        request.app.state.PYGEOAPI.api,
        pygeoapi.api.tiles.get_collection_tiles,
        request,
        collection_id
    )


async def get_collection_tiles_metadata(request: Request, collection_id=None,
                                        tileMatrixSetId=None):
    """
    OGC open api collection tiles service metadata

    :param collection_id: collection identifier
    :param tileMatrixSetId: identifier of tile matrix set

    :returns: HTTP response
    """
    if 'collection_id' in request.path_params:
        collection_id = request.path_params['collection_id']
    if 'tileMatrixSetId' in request.path_params:
        tileMatrixSetId = request.path_params['tileMatrixSetId']

    return await execute_from_starlette(
        request.app.state.PYGEOAPI.api,
        pygeoapi.api.tiles.get_collection_tiles_metadata, request,
        collection_id, tileMatrixSetId, skip_valid_check=True,
    )


async def get_collection_items_tiles(request: Request, collection_id=None,
                                     tileMatrixSetId=None, tile_matrix=None,
                                     tileRow=None, tileCol=None):
    """
    OGC open api collection tiles service

    :param request: Starlette Request instance
    :param collection_id: collection identifier
    :param tileMatrixSetId: identifier of tile matrix set
    :param tile_matrix: identifier of {z} matrix index
    :param tileRow: identifier of {y} matrix index
    :param tileCol: identifier of {x} matrix index

    :returns: HTTP response
    """
    if 'collection_id' in request.path_params:
        collection_id = request.path_params['collection_id']
    if 'tileMatrixSetId' in request.path_params:
        tileMatrixSetId = request.path_params['tileMatrixSetId']
    if 'tile_matrix' in request.path_params:
        tile_matrix = request.path_params['tile_matrix']
    if 'tileRow' in request.path_params:
        tileRow = request.path_params['tileRow']
    if 'tileCol' in request.path_params:
        tileCol = request.path_params['tileCol']
    return await execute_from_starlette(
        request.app.state.PYGEOAPI.api,
        pygeoapi.api.tiles.get_collection_tiles_data, request, collection_id,
        tileMatrixSetId, tile_matrix, tileRow, tileCol,
        skip_valid_check=True,
    )


async def collection_items(request: Request, collection_id=None, item_id=None):
    """
    OGC API collections items endpoint

    :param request: Starlette Request instance
    :param collection_id: collection identifier
    :param item_id: item identifier

    :returns: Starlette HTTP Response
    """

    if 'collection_id' in request.path_params:
        collection_id = request.path_params['collection_id']
    if 'item_id' in request.path_params:
        item_id = request.path_params['item_id']
    if item_id is None:
        if request.method == 'POST':  # filter or manage items
            content_type = request.headers.get('content-type')
            if content_type is not None:
                if content_type == 'application/geo+json':
                    return await execute_from_starlette(
                        request.app.state.PYGEOAPI.api,
                        pygeoapi.api.itemtypes.manage_collection_item, request,
                        'create', collection_id, skip_valid_check=True)
                else:
                    return await execute_from_starlette(
                        request.app.state.PYGEOAPI.api,
                        pygeoapi.api.itemtypes.get_collection_items,
                        request,
                        collection_id,
                        skip_valid_check=True,
                    )
        elif request.method == 'OPTIONS':
            return await execute_from_starlette(
                request.app.state.PYGEOAPI.api,
                pygeoapi.api.itemtypes.manage_collection_item, request,
                'options', collection_id, skip_valid_check=True,
            )
        else:  # GET: list items
            return await execute_from_starlette(
                request.app.state.PYGEOAPI.api,
                pygeoapi.api.itemtypes.get_collection_items,
                request, collection_id,
                skip_valid_check=True)

    elif request.method == 'DELETE':
        return await execute_from_starlette(
            request.app.state.PYGEOAPI.api,
            pygeoapi.api.itemtypes.manage_collection_item,
            request, 'delete',
            collection_id, item_id, skip_valid_check=True,
        )
    elif request.method == 'PUT':
        return await execute_from_starlette(
            request.app.state.PYGEOAPI.api,
            pygeoapi.api.itemtypes.manage_collection_item,
            request, 'update',
            collection_id, item_id, skip_valid_check=True,
        )
    elif request.method == 'OPTIONS':
        return await execute_from_starlette(
            request.app.state.PYGEOAPI.api,
            pygeoapi.api.itemtypes.manage_collection_item,
            request, 'options',
            collection_id, item_id, skip_valid_check=True,
        )
    else:
        return await execute_from_starlette(
            request.app.state.PYGEOAPI.api,
            pygeoapi.api.itemtypes.get_collection_item, request,
            collection_id, item_id)


async def collection_coverage(request: Request, collection_id=None):
    """
    OGC API - Coverages coverage endpoint

    :param request: Starlette Request instance
    :param collection_id: collection identifier

    :returns: Starlette HTTP Response
    """
    if 'collection_id' in request.path_params:
        collection_id = request.path_params['collection_id']

    return await execute_from_starlette(
        request.app.state.PYGEOAPI.api,
        pygeoapi.api.coverages.get_collection_coverage,
        request, collection_id,
        skip_valid_check=True
    )


async def collection_map(request: Request, collection_id=None, style_id=None):
    """
    OGC API - Maps map render endpoint

    :param collection_id: collection identifier
    :param style_id: style identifier

    :returns: HTTP response
    """

    if 'collection_id' in request.path_params:
        collection_id = request.path_params['collection_id']
    if 'style_id' in request.path_params:
        style_id = request.path_params['style_id']

    return await execute_from_starlette(
        request.app.state.PYGEOAPI.api,
        pygeoapi.api.maps.get_collection_map,
        request, collection_id, style_id
    )


async def get_processes(request: Request, process_id=None):
    """
    OGC API - Processes description endpoint

    :param request: Starlette Request instance
    :param process_id: identifier of process to describe

    :returns: Starlette HTTP Response
    """
    if 'process_id' in request.path_params:
        process_id = request.path_params['process_id']

    return await execute_from_starlette(
        request.app.state.PYGEOAPI.api,
        pygeoapi.api.processes.describe_processes,
        request, process_id
    )


async def get_jobs(request: Request, job_id=None):
    """
    OGC API - Processes jobs endpoint

    :param request: Starlette Request instance
    :param job_id: job identifier

    :returns: Starlette HTTP Response
    """

    if 'job_id' in request.path_params:
        job_id = request.path_params['job_id']

    if job_id is None:  # list of submit job
        return await execute_from_starlette(
            request.app.state.PYGEOAPI.api,
            pygeoapi.api.processes.get_jobs,
            request
        )
    else:  # get or delete job
        if request.method == 'DELETE':
            return await execute_from_starlette(
                request.app.state.PYGEOAPI.api,
                pygeoapi.api.processes.delete_job,
                request,
                job_id
            )
        else:  # Return status of a specific job
            return await execute_from_starlette(
                request.app.state.PYGEOAPI.api,
                pygeoapi.api.processes.get_jobs,
                request,
                job_id
            )


async def execute_process_jobs(request: Request, process_id=None):
    """
    OGC API - Processes jobs endpoint

    :param request: Starlette Request instance
    :param process_id: process identifier

    :returns: Starlette HTTP Response
    """

    if 'process_id' in request.path_params:
        process_id = request.path_params['process_id']

    return await execute_from_starlette(
        request.app.state.PYGEOAPI.api,
        pygeoapi.api.processes.execute_process,
        request, process_id
    )


async def get_job_result(request: Request, job_id=None):
    """
    OGC API - Processes job result endpoint

    :param request: Starlette Request instance
    :param job_id: job identifier

    :returns: HTTP response
    """

    if 'job_id' in request.path_params:
        job_id = request.path_params['job_id']

    return await execute_from_starlette(
        request.app.state.PYGEOAPI.api,
        pygeoapi.api.processes.get_job_result,
        request, job_id
    )


async def get_collection_edr_query(request: Request, collection_id=None, instance_id=None, location_id=None):  # noqa
    """
    OGC EDR API endpoints

    :param collection_id: collection identifier
    :param instance_id: instance identifier
    :param location_id: location id of a /locations/<location_id> query

    :returns: HTTP response
    """

    if 'collection_id' in request.path_params:
        collection_id = request.path_params['collection_id']

    if 'instance_id' in request.path_params:
        instance_id = request.path_params['instance_id']

    if (request.url.path.endswith('instances') or
            (instance_id is not None and
             request.url.path.endswith(instance_id))):
        return await execute_from_starlette(
            request.app.state.PYGEOAPI.api,
            pygeoapi.api.environmental_data_retrieval.get_collection_edr_instances,
            request, collection_id,
            instance_id
        )

    if 'location_id' in request.path_params:
        location_id = request.path_params['location_id']
        query_type = 'locations'
    else:
        query_type = request['path'].split('/')[-1]

    return await execute_from_starlette(
        request.app.state.PYGEOAPI.api,
        pygeoapi.api.environmental_data_retrieval.get_collection_edr_query,
        request, collection_id,
        instance_id, query_type, location_id,
        skip_valid_check=True,
    )


async def collections(request: Request, collection_id=None):
    """
    OGC API collections endpoint

    :param request: Starlette Request instance
    :param collection_id: collection identifier

    :returns: Starlette HTTP Response
    """
    if 'collection_id' in request.path_params:
        collection_id = request.path_params['collection_id']

    return await execute_from_starlette(
        request.app.state.PYGEOAPI.api,
        pygeoapi.api.describe_collections,
        request,
        collection_id
    )


async def stac_catalog_root(request: Request):
    """
    STAC root endpoint

    :param request: Starlette Request instance

    :returns: Starlette HTTP response
    """
    return await execute_from_starlette(
        request.app.state.PYGEOAPI.api,
        pygeoapi.api.stac.get_stac_root,
        request
    )


async def stac_catalog_path(request: Request):
    """
    STAC endpoint

    :param request: Starlette Request instance

    :returns: Starlette HTTP response
    """
    path = request.path_params["path"]
    return await execute_from_starlette(
        request.app.state.PYGEOAPI.api,
        pygeoapi.api.stac.get_stac_path,
        request,
        path
    )


routes = [
    Route('/', landing_page),
    Route('/openapi', openapi),
    Route('/conformance', conformance),
    Route('/TileMatrixSets/{tileMatrixSetId}', get_tilematrix_set),
    Route('/TileMatrixSets', get_tilematrix_sets),
    Route('/collections/{collection_id:path}/schema', collection_schema),
    Route('/collections/{collection_id:path}/queryables', collection_queryables),  # noqa
    Route('/collections/{collection_id:path}/tiles', get_collection_tiles),
    Route('/collections/{collection_id:path}/tiles/{tileMatrixSetId}', get_collection_tiles_metadata),  # noqa
    Route('/collections/{collection_id:path}/tiles/{tileMatrixSetId}/metadata', get_collection_tiles_metadata),  # noqa
    Route('/collections/{collection_id:path}/tiles/{tileMatrixSetId}/{tile_matrix}/{tileRow}/{tileCol}', get_collection_items_tiles),  # noqa
    Route('/collections/{collection_id:path}/items', collection_items, methods=['GET', 'POST', 'OPTIONS']),  # noqa
    Route('/collections/{collection_id:path}/items/{item_id:path}', collection_items, methods=['GET', 'PUT', 'DELETE', 'OPTIONS']),  # noqa
    Route('/collections/{collection_id:path}/coverage', collection_coverage),  # noqa
    Route('/collections/{collection_id:path}/map', collection_map),
    Route('/collections/{collection_id:path}/styles/{style_id:path}/map', collection_map),  # noqa
    Route('/processes', get_processes),
    Route('/processes/{process_id}', get_processes),
    Route('/jobs', get_jobs),
    Route('/jobs/{job_id}', get_jobs, methods=['GET', 'DELETE']),
    Route('/processes/{process_id}/execution', execute_process_jobs, methods=['POST']),  # noqa
    Route('/jobs/{job_id}/results', get_job_result),
    Route('/collections/{collection_id:path}/position', get_collection_edr_query),  # noqa
    Route('/collections/{collection_id:path}/area', get_collection_edr_query),
    Route('/collections/{collection_id:path}/cube', get_collection_edr_query),
    Route('/collections/{collection_id:path}/radius', get_collection_edr_query),  # noqa
    Route('/collections/{collection_id:path}/trajectory', get_collection_edr_query),  # noqa
    Route('/collections/{collection_id:path}/corridor', get_collection_edr_query),  # noqa
    Route('/collections/{collection_id:path}/locations', get_collection_edr_query),  # noqa
    Route('/collections/{collection_id:path}/locations/{location_id}', get_collection_edr_query),  # noqa
    Route('/collections/{collection_id:path}/instances', get_collection_edr_query),  # noqa
    Route('/collections/{collection_id:path}/instances/{instance_id}', get_collection_edr_query),  # noqa
    Route('/collections/{collection_id:path}/instances/{instance_id}/position', get_collection_edr_query),  # noqa
    Route('/collections/{collection_id:path}/instances/{instance_id}/area', get_collection_edr_query),  # noqa
    Route('/collections/{collection_id:path}/instances/{instance_id}/cube', get_collection_edr_query),  # noqa
    Route('/collections/{collection_id:path}/instances/{instance_id}/radius', get_collection_edr_query),  # noqa
    Route('/collections/{collection_id:path}/instances/{instance_id}/trajectory', get_collection_edr_query),  # noqa
    Route('/collections/{collection_id:path}/instances/{instance_id}/corridor', get_collection_edr_query),  # noqa
    Route('/collections/{collection_id:path}/instances/{instance_id}/locations', get_collection_edr_query),  # noqa
    Route('/collections/{collection_id:path}/instances/{instance_id}/locations/{location_id}', get_collection_edr_query),  # noqa
    Route('/collections', collections),
    Route('/collections/{collection_id:path}', collections),
    Route('/stac', stac_catalog_root),
    Route('/stac/{path:path}', stac_catalog_path)
]
