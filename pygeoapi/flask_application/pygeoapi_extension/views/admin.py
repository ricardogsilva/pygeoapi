import flask

import pygeoapi.api
import pygeoapi.admin
from pygeoapi.flask_application.pygeoapi_extension.views.util import execute_from_flask

blueprint = flask.Blueprint('admin', __name__)


def configure_blueprint(
        pygeoapi_api: pygeoapi.api.API,  # noqa
        pygeoapi_admin: pygeoapi.admin.Admin,  # noqa
        static_folder: str, url_prefix: str
) -> None:
    global blueprint
    blueprint.static_folder = static_folder
    blueprint.url_prefix = url_prefix
    # enable/disable blueprint routes based on the pygeoapi api and admin


@blueprint.route('/admin/config', methods=['GET', 'PUT', 'PATCH'])
def admin_config():
    """
    Admin endpoint

    :returns: HTTP response
    """

    if flask.request.method == 'GET':
        return execute_from_flask(
            flask.current_app.extensions['pygeoapi']['admin_api'],
            pygeoapi.admin.get_config_,
            flask.request
        )

    elif flask.request.method == 'PUT':
        return execute_from_flask(
            flask.current_app.extensions['pygeoapi']['admin_api'],
            pygeoapi.admin.put_config, flask.request,
        )

    elif flask.request.method == 'PATCH':
        return execute_from_flask(
            flask.current_app.extensions['pygeoapi']['admin_api'],
            pygeoapi.admin.patch_config,
            flask.request,
        )


@blueprint.route('/admin/config/resources', methods=['GET', 'POST'])
def admin_config_resources():
    """
    Resources endpoint

    :returns: HTTP response
    """

    if flask.request.method == 'GET':
        return execute_from_flask(
            flask.current_app.extensions['pygeoapi']['admin_api'],
            pygeoapi.admin.get_resources, flask.request)

    elif flask.request.method == 'POST':
        return execute_from_flask(
            flask.current_app.extensions['pygeoapi']['admin_api'],
            pygeoapi.admin.post_resource, flask.request)


@blueprint.route(
    '/admin/config/resources/<resource_id>',
    methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def admin_config_resource(resource_id):
    """
    Resource endpoint

    :returns: HTTP response
    """

    if flask.request.method == 'GET':
        return execute_from_flask(
            flask.current_app.extensions['pygeoapi']['admin_api'],
            pygeoapi.admin.get_resource,
            flask.request,
            resource_id
        )

    elif flask.request.method == 'DELETE':
        return execute_from_flask(
            flask.current_app.extensions['pygeoapi']['admin_api'],
            pygeoapi.admin.delete_resource,
            flask.request,
            resource_id
        )

    elif flask.request.method == 'PUT':
        return execute_from_flask(
            flask.current_app.extensions['pygeoapi']['admin_api'],
            pygeoapi.admin.put_resource,
            flask.request,
            resource_id
        )

    elif flask.request.method == 'PATCH':
        return execute_from_flask(
            flask.current_app.extensions['pygeoapi']['admin_api'],
            pygeoapi.admin.patch_resource,
            flask.request,
            resource_id
        )
