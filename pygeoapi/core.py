"""Proof-of-concept (POC) for RFC2.

TODO in order to be able to demo this POC:

- Implement pygeoapi as a flask extension

- pygeoapi must drop support for Python v3.7, as the `referencing`
  third-party package being used here only supports Python 3.8+
- pygeoapi must drop the `datamodel-code-generator` dependency, as it prevents
  installation of a more recent version of `jsonschema` which is required in
  order to work with schema registries
"""
import abc
import dataclasses
import flask
import logging
import os
import yaml
import referencing.jsonschema
from jsonschema import Draft202012Validator
from referencing import (
    Registry,
    Resource,
)
from pathlib import Path
from typing import Dict, List, Optional

LOGGER = logging.getLogger(__name__)


def build_schema_registry(
        current_dir: Path,
        base_dir: Optional[Path] = None,
        registry: Optional[Registry] = None,
) -> Registry:
    base_dir = base_dir if base_dir is not None else current_dir
    if registry is None:
        registry = Registry()
    for child in current_dir.iterdir():
        if child.is_file():
            LOGGER.debug(f"Processing {child}...")
            parsed = yaml.safe_load(child.read_text())
            if child.name == "processList.yaml":
                LOGGER.debug(f"Initially parsed contents: {parsed!r}")
            # replace whatever $refs may be contained in `parsed` with
            # a proper namespaced $ref that is rooted on base_dir
            _replace_refs_in_schema(
                parsed,
                current_dir=current_dir,
                base_dir=base_dir,
            )
            if child.name == "processList.yaml":
                LOGGER.debug(f"Parsed contents after $ref modification: {parsed!r}")
            registry = registry.with_resource(
                uri=str(child.resolve().relative_to(base_dir)),
                resource=Resource(
                    contents=parsed,
                    specification=referencing.jsonschema.DRAFT202012
                )
            )
            registry = registry.crawl()
        elif child.is_dir():
            LOGGER.debug(f"Descending into {child}...")
            registry = build_schema_registry(
                child, base_dir=base_dir, registry=registry)
    return registry


def _replace_refs_in_schema(
        the_dict: Dict,
        current_dir: Path,
        base_dir: Path,
):
    """Traverse the input schema dict and replace `$ref` entries.

    This function exists in order to overcome a percieved difficulty in
    wokring with the official OGC API schemas - these use relative filesystem
    paths in their `$ref` properties, whereby the paths are relative to their
    own directory, and not relative to some common base path.

    `$ref` entries will be replaced by a relative path
    """
    for key, value in the_dict.items():
        if key == "$ref" and isinstance(value, str):
            try:
                new_value = str((current_dir / value).resolve().relative_to(base_dir))
            except ValueError:
                LOGGER.warning(
                    f"Unable to find relative path from the base dir for "
                    f"{value!r}, trying its parent dir as a last resort..."
                )
                new_value = str(
                    (current_dir / value).resolve()
                    .relative_to(base_dir.parent)
                )
            the_dict[key] = new_value
        elif isinstance(value, dict):
            _replace_refs_in_schema(the_dict[key], current_dir, base_dir)


@dataclasses.dataclass
class PygeoApiProcess:
    """Pygeoapi internal process representation.

    For the purpose of this POC, we add some irrelevant properties, just to
    demo how internal details of pygeoapi need not be exposed to the outside
    world.
    """
    id: str
    some_detail: Optional[str] = None
    another_detail: Optional[str] = None


class PyGeoApiSchema(abc.ABC):

    @property
    @abc.abstractmethod
    def schema_uri(self) -> Optional[str]:
        """Implement this as a class variable or as a method in child classes."""

    @abc.abstractmethod
    def as_dict(self) -> Dict:
        """Implement this method in child classes."""


@dataclasses.dataclass
class PyGeoApiDataClassSchema(PyGeoApiSchema, abc.ABC):

    def as_dict(self):
        naive = dataclasses.asdict(self)
        del naive["schema_uri"]
        return {k: v for k, v in naive.items() if v is not None}


@dataclasses.dataclass
class ProcessSummary(PyGeoApiDataClassSchema):
    id: str
    version: str
    schema_uri: str = "processes-core/processSummary.yaml"


@dataclasses.dataclass
class Link(PyGeoApiDataClassSchema):
    href: str
    rel: Optional[str] = None
    type: Optional[str] = None
    hreflang: Optional[str] = None
    title: Optional[str] = None
    schema_uri: str = "common-core/link.yaml"


@dataclasses.dataclass
class ProcessList(PyGeoApiDataClassSchema):
    processes: List[ProcessSummary] = dataclasses.field(default_factory=list)
    links: List[Link] = dataclasses.field(default_factory=list)
    schema_uri: str = "processes-core/processList.yaml"

    def as_dict(self) -> Dict:
        return {
            "processes": [p.as_dict() for p in self.processes],
            "links": [li.as_dict() for li in self.links]
        }


class ProcessManager:

    def list_processes(self, limit: int) -> List[PygeoApiProcess]:
        # a crude implementation for brevity reasons only, as process
        # internals are not relevant to the RFC scope
        return [
            PygeoApiProcess(id="hello-world1", some_detail="irrelevant"),
            PygeoApiProcess(id="hello-world2", some_detail="irrelevant"),
            PygeoApiProcess(id="hello-world3", some_detail="irrelevant"),
            PygeoApiProcess(id="hello-world4", some_detail="irrelevant"),
        ][:limit]


class Api:

    def __init__(self, schemas_base_dir: Path):
        self.manager = ProcessManager()
        self.schema_registry = build_schema_registry(schemas_base_dir)

    def list_processes(self, limit: Optional[int] = 100) -> ProcessList:
        result = ProcessList()
        for process_detail in self.manager.list_processes(limit=limit):
            summary = ProcessSummary(
                id=process_detail.id,
                version="0.1.0"
            )
            result.processes.append(summary)
        result.links.append(
            Link(href="some-relevant-url")
        )
        return result

    def validate(self, response: PyGeoApiSchema):
        schema = self.schema_registry[response.schema_uri].contents
        validator = Draft202012Validator(schema, registry=self.schema_registry)
        return validator.validate(response.as_dict())


pygeoapi_blueprint = flask.Blueprint("pygeoapi", __name__)


@pygeoapi_blueprint.route("/processes")
def list_processes():
    limit = int(
        flask.request.args.get(
            "limit", flask.current_app.config["PYGEOAPI_LIMIT"]
        )
    )
    api = flask.current_app.extensions["pygeoapi"]["api"]
    response = api.list_processes(limit)
    if flask.current_app.config["PYGEOAPI_VALIDATE_RESPONSES"]:
        api.validate(response)
    return response.as_dict()


def create_app(blueprints):
    # for brevity, a very simple way to pass configuration to the flask application
    app = flask.Flask(__name__)
    app.config["PYGEOAPI_SCHEMAS_BASE_DIR"] = Path(
        os.getenv("PYGEOAPI__OGC_API_PROCESSES_SCHEMAS_BASE_DIR"))
    app.config["PYGEOAPI_LIMIT"] = 100
    app.config["PYGEOAPI_VALIDATE_RESPONSES"] = True
    app.extensions["pygeoapi"] = {"api": Api(app.config["PYGEOAPI_SCHEMAS_BASE_DIR"])}
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
    return app


app = create_app([pygeoapi_blueprint])
app.run("0.0.0.0", port=8000, debug=True)
