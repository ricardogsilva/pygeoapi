import flask

from ....core import Api

blueprint = flask.Blueprint(
    "pygeoapi",
    __name__,
    template_folder="templates",
    static_folder="static",
)


@blueprint.context_processor
def inject_pygeoapi_details():
    api: Api = flask.current_app.extensions["pygeoapi"]["api"]
    return {
        "pygeoapi_identification": api.identification,
        "pygeoapi_license": api.license,
        "pygeoapi_point_of_contact": api.point_of_contact,
        "pygeoapi_provider": api.provider,
    }
