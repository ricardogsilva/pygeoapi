import flask

import pygeoapi.api
import pygeoapi.api.itemtypes
import pygeoapi.api.tiles
from pygeoapi.flask_application.pygeoapi_extension.views.util import execute_from_flask

blueprint = flask.Blueprint('pygeoapi', __name__)


def configure_blueprint(static_folder: str, url_prefix: str) -> None:
    global blueprint
    blueprint.static_folder = static_folder
    blueprint.url_prefix = url_prefix


@blueprint.route('/')
def landing_page():
    """
    OGC API landing page endpoint

    :returns: HTTP response
    """
    return execute_from_flask(
        flask.current_app.config['pygeoapi']['api'],
        pygeoapi.api.landing_page,
        flask.request
    )


@blueprint.route('/openapi')
def openapi():
    """
    OpenAPI endpoint

    :returns: HTTP response
    """

    return execute_from_flask(
        flask.current_app.config['pygeoapi']['api'],
        pygeoapi.api.openapi_,
        flask.request
    )


@blueprint.route('/conformance')
def conformance():
    """
    OGC API conformance endpoint

    :returns: HTTP response
    """

    return execute_from_flask(
        flask.current_app.config['pygeoapi']['api'],
        pygeoapi.api.conformance,
        flask.request
    )


@blueprint.route('/TileMatrixSets/<tileMatrixSetId>')
def get_tilematrix_set(tileMatrixSetId=None):
    """
    OGC API TileMatrixSet endpoint

    :param tileMatrixSetId: identifier of tile matrix set

    :returns: HTTP response
    """

    return execute_from_flask(
        flask.current_app.config['pygeoapi']['api'],
        pygeoapi.api.tiles.tilematrixset,
        flask.request,
        tileMatrixSetId,
    )


@blueprint.route('/TileMatrixSets')
def get_tilematrix_sets():
    """
    OGC API TileMatrixSets endpoint

    :returns: HTTP response
    """

    return execute_from_flask(
        flask.current_app.config['pygeoapi']['api'],
        pygeoapi.api.tiles.tilematrixsets,
        flask.request
    )


@blueprint.route('/collections')
@blueprint.route('/collections/<path:collection_id>')
def collections(collection_id=None):
    """
    OGC API collections endpoint

    :param collection_id: collection identifier

    :returns: HTTP response
    """

    return execute_from_flask(
        flask.current_app.config['pygeoapi']['api'],
        pygeoapi.api.describe_collections,
        flask.request,
        collection_id
    )


@blueprint.route('/collections/<path:collection_id>/schema')
def collection_schema(collection_id):
    """
    OGC API - collections schema endpoint

    :param collection_id: collection identifier

    :returns: HTTP response
    """

    return execute_from_flask(
        flask.current_app.config['pygeoapi']['api'],
        pygeoapi.api.get_collection_schema,
        flask.request,
        collection_id
    )


@blueprint.route('/collections/<path:collection_id>/queryables')
def collection_queryables(collection_id=None):
    """
    OGC API collections queryables endpoint

    :param collection_id: collection identifier

    :returns: HTTP response
    """

    return execute_from_flask(
        flask.current_app.config['pygeoapi']['api'],
        pygeoapi.api.itemtypes.get_collection_queryables,
        flask.request,
        collection_id
    )


@blueprint.route('/collections/<path:collection_id>/items',
                 methods=['GET', 'POST', 'OPTIONS'],
                 provide_automatic_options=False)
@blueprint.route('/collections/<path:collection_id>/items/<path:item_id>',
                 methods=['GET', 'PUT', 'DELETE', 'OPTIONS'],
                 provide_automatic_options=False)
def collection_items(collection_id, item_id=None):
    """
    OGC API collections items endpoint

    :param collection_id: collection identifier
    :param item_id: item identifier

    :returns: HTTP response
    """

    if item_id is None:
        if request.method == 'POST':  # filter or manage items
            if request.content_type is not None:
                if request.content_type == 'application/geo+json':
                    return execute_from_flask(
                        itemtypes_api.manage_collection_item,
                        request, 'create', collection_id,
                        skip_valid_check=True)
                else:
                    return execute_from_flask(
                        itemtypes_api.get_collection_items, request,
                        collection_id, skip_valid_check=True)
        elif request.method == 'OPTIONS':
            return execute_from_flask(
                itemtypes_api.manage_collection_item, request, 'options',
                collection_id, skip_valid_check=True)
        else:  # GET: list items
            return execute_from_flask(itemtypes_api.get_collection_items,
                                      request, collection_id,
                                      skip_valid_check=True)

    elif request.method == 'DELETE':
        return execute_from_flask(itemtypes_api.manage_collection_item,
                                  request, 'delete', collection_id, item_id,
                                  skip_valid_check=True)
    elif request.method == 'PUT':
        return execute_from_flask(itemtypes_api.manage_collection_item,
                                  request, 'update', collection_id, item_id,
                                  skip_valid_check=True)
    elif request.method == 'OPTIONS':
        return execute_from_flask(itemtypes_api.manage_collection_item,
                                  request, 'options', collection_id, item_id,
                                  skip_valid_check=True)
    else:
        return execute_from_flask(itemtypes_api.get_collection_item, request,
                                  collection_id, item_id)


@blueprint.route('/collections/<path:collection_id>/coverage')
def collection_coverage(collection_id):
    """
    OGC API - Coverages coverage endpoint

    :param collection_id: collection identifier

    :returns: HTTP response
    """

    return execute_from_flask(coverages_api.get_collection_coverage, request,
                              collection_id, skip_valid_check=True)


@blueprint.route('/collections/<path:collection_id>/tiles')
def get_collection_tiles(collection_id=None):
    """
    OGC open api collections tiles access point

    :param collection_id: collection identifier

    :returns: HTTP response
    """

    return execute_from_flask(tiles_api.get_collection_tiles, request,
                              collection_id)


@blueprint.route('/collections/<path:collection_id>/tiles/<tileMatrixSetId>')
@blueprint.route('/collections/<path:collection_id>/tiles/<tileMatrixSetId>/metadata')  # noqa
def get_collection_tiles_metadata(collection_id=None, tileMatrixSetId=None):
    """
    OGC open api collection tiles service metadata

    :param collection_id: collection identifier
    :param tileMatrixSetId: identifier of tile matrix set

    :returns: HTTP response
    """

    return execute_from_flask(tiles_api.get_collection_tiles_metadata,
                              request, collection_id, tileMatrixSetId,
                              skip_valid_check=True)


@blueprint.route('/collections/<path:collection_id>/tiles/\
<tileMatrixSetId>/<tileMatrix>/<tileRow>/<tileCol>')
def get_collection_tiles_data(collection_id=None, tileMatrixSetId=None,
                              tileMatrix=None, tileRow=None, tileCol=None):
    """
    OGC open api collection tiles service data

    :param collection_id: collection identifier
    :param tileMatrixSetId: identifier of tile matrix set
    :param tileMatrix: identifier of {z} matrix index
    :param tileRow: identifier of {y} matrix index
    :param tileCol: identifier of {x} matrix index

    :returns: HTTP response
    """

    return execute_from_flask(
        tiles_api.get_collection_tiles_data,
        request, collection_id, tileMatrixSetId, tileMatrix, tileRow, tileCol,
        skip_valid_check=True,
    )


@blueprint.route('/collections/<collection_id>/map')
@blueprint.route('/collections/<collection_id>/styles/<style_id>/map')
def collection_map(collection_id, style_id=None):
    """
    OGC API - Maps map render endpoint

    :param collection_id: collection identifier
    :param style_id: style identifier

    :returns: HTTP response
    """

    return execute_from_flask(
        maps_api.get_collection_map, request, collection_id, style_id
    )


@blueprint.route('/processes')
@blueprint.route('/processes/<process_id>')
def get_processes(process_id=None):
    """
    OGC API - Processes description endpoint

    :param process_id: process identifier

    :returns: HTTP response
    """

    return execute_from_flask(processes_api.describe_processes, request,
                              process_id)


@blueprint.route('/jobs')
@blueprint.route('/jobs/<job_id>',
                 methods=['GET', 'DELETE'])
def get_jobs(job_id=None):
    """
    OGC API - Processes jobs endpoint

    :param job_id: job identifier

    :returns: HTTP response
    """

    if job_id is None:
        return execute_from_flask(processes_api.get_jobs, request)
    else:
        if request.method == 'DELETE':  # dismiss job
            return execute_from_flask(processes_api.delete_job, request,
                                      job_id)
        else:  # Return status of a specific job
            return execute_from_flask(processes_api.get_jobs, request, job_id)


@blueprint.route('/processes/<process_id>/execution', methods=['POST'])
def execute_process_jobs(process_id):
    """
    OGC API - Processes execution endpoint

    :param process_id: process identifier

    :returns: HTTP response
    """

    return execute_from_flask(processes_api.execute_process, request,
                              process_id)


@blueprint.route('/jobs/<job_id>/results',
                 methods=['GET'])
def get_job_result(job_id=None):
    """
    OGC API - Processes job result endpoint

    :param job_id: job identifier

    :returns: HTTP response
    """

    return execute_from_flask(processes_api.get_job_result, request, job_id)


@blueprint.route('/collections/<path:collection_id>/position')
@blueprint.route('/collections/<path:collection_id>/area')
@blueprint.route('/collections/<path:collection_id>/cube')
@blueprint.route('/collections/<path:collection_id>/radius')
@blueprint.route('/collections/<path:collection_id>/trajectory')
@blueprint.route('/collections/<path:collection_id>/corridor')
@blueprint.route('/collections/<path:collection_id>/locations/<location_id>')
@blueprint.route('/collections/<path:collection_id>/locations')
@blueprint.route('/collections/<path:collection_id>/instances/<instance_id>/position')  # noqa
@blueprint.route('/collections/<path:collection_id>/instances/<instance_id>/area')  # noqa
@blueprint.route('/collections/<path:collection_id>/instances/<instance_id>/cube')  # noqa
@blueprint.route('/collections/<path:collection_id>/instances/<instance_id>/radius')  # noqa
@blueprint.route('/collections/<path:collection_id>/instances/<instance_id>/trajectory')  # noqa
@blueprint.route('/collections/<path:collection_id>/instances/<instance_id>/corridor')  # noqa
@blueprint.route('/collections/<path:collection_id>/instances/<instance_id>/locations/<location_id>')  # noqa
@blueprint.route('/collections/<path:collection_id>/instances/<instance_id>/locations')  # noqa
@blueprint.route('/collections/<path:collection_id>/instances/<instance_id>')
@blueprint.route('/collections/<path:collection_id>/instances')
def get_collection_edr_query(collection_id, instance_id=None,
                             location_id=None):
    """
    OGC EDR API endpoints

    :param collection_id: collection identifier
    :param instance_id: instance identifier
    :param location_id: location id of a /locations/<location_id> query

    :returns: HTTP response
    """

    if (request.path.endswith('instances') or
            (instance_id is not None and
             request.path.endswith(instance_id))):
        return execute_from_flask(
            edr_api.get_collection_edr_instances, request, collection_id,
            instance_id
        )

    if location_id:
        query_type = 'locations'
    else:
        query_type = request.path.split('/')[-1]

    return execute_from_flask(
        edr_api.get_collection_edr_query, request, collection_id, instance_id,
        query_type, location_id, skip_valid_check=True
    )


@blueprint.route('/stac')
def stac_catalog_root():
    """
    STAC root endpoint

    :returns: HTTP response
    """

    return execute_from_flask(stac_api.get_stac_root, request)


@blueprint.route('/stac/<path:path>')
def stac_catalog_path(path):
    """
    STAC path endpoint

    :param path: path

    :returns: HTTP response
    """

    return execute_from_flask(stac_api.get_stac_path, request, path)
