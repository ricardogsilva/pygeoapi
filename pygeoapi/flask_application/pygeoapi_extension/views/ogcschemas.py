import os

import flask

from pygeoapi.util import get_mimetype

blueprint = flask.Blueprint('ogcschemas', __name__)


@blueprint.route('/schemas/<path:path>', methods=['GET'])
def schemas(path):
    """
    Serve OGC schemas locally

    :param path: path of the OGC schema document

    :returns: HTTP response
    """

    pygeoapi_api = flask.current_app.extensions['pygeoapi']['api']
    ogc_schemas_location = pygeoapi_api.config['server'].get('ogc_schemas_location')
    full_filepath = os.path.join(ogc_schemas_location, path)
    dirname_ = os.path.dirname(full_filepath)
    basename_ = os.path.basename(full_filepath)

    path_ = dirname_.replace('..', '').replace('//', '').replace('./', '')

    if '..' in path_:
        return 'Invalid path', 400

    return flask.send_from_directory(
        path_, basename_, mimetype=get_mimetype(basename_))
