"""Proof-of-concept (POC) for RFC2.

This POC defines:

- an internal model for a pygeoapi process
- the PyGeoApiSchema abstract class


usage:

>>> from pygeoapi.core import Api
>>> # before instantiating the api we would load some configuration
>>> api = Api()
>>> list_processes_response = api.list_processes()
>>> api.validate(list_processes_response)
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

import jsonschema


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
        ...

    @abc.abstractmethod
    def as_dict(self) -> Dict:
        ...

    # def validate(self, schema_registry: Registry):
    #     """Validate this instance against its own schema."""
    #     schema = schema_registry[self.schema_uri].contents
    #     validator = Draft202012Validator(schema, registry=schema_registry)
    #     return validator.validate(self.as_dict())


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
            PygeoApiProcess(id="hello-world", some_detail="irrelevant")
        ]


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
    limit = flask.request.args.get("limit")
    api = flask.current_app.extensions["pygeoapi"]["api"]
    response = api.list_processes(limit)
    return response.as_dict()


def create_app(blueprints):
    schemas_base_dir = Path(
        os.getenv("PYGEOAPI__OGC_API_PROCESSES_SCHEMAS_BASE_DIR"))
    app = flask.Flask(__name__)
    app.extensions["pygeoapi"] = {"api": Api(schemas_base_dir)}
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
    return app


app = create_app([pygeoapi_blueprint])
app.run("0.0.0.0", port=8000, debug=True)
