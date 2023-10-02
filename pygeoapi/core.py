"""Proof-of-concept (POC) for RFC2.

This POC defines:

- an internal model for a pygeoapi process
- the PyGeoApiSchema abstract class


usage:

>>> from pygeoapi.core import Api
>>> # before instantiating the api we would load some configuration
>>> api = Api()
>>> processes = api.list_processes()
>>> processes.validate()
"""
import abc
import dataclasses
import json
from pathlib import Path
from typing import Dict, List, Optional

import jsonschema


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
    def schema_path(self) -> Optional[Path]:
        ...

    @property
    def schema(self) -> Optional[Dict]:
        if self.schema_path is not None:
            return json.loads(self.schema_path.read_text())

    def validate(self):
        """Validate this instance against its own schema."""
        return jsonschema.validate(instance=self.as_dict(), schema=self.schema)

    @abc.abstractmethod
    def as_dict(self) -> Dict:
        ...


@dataclasses.dataclass
class PyGeoApiDataClassSchema(PyGeoApiSchema, abc.ABC):

    def as_dict(self):
        return dataclasses.asdict(self)


@dataclasses.dataclass
class ProcessSummary(PyGeoApiDataClassSchema):
    id: str
    version: str
    schema_path: Optional[Path] = None


@dataclasses.dataclass
class Link(PyGeoApiDataClassSchema):
    href: str
    rel: Optional[str] = None
    type: Optional[str] = None
    hreflang: Optional[str] = None
    title: Optional[str] = None
    schema_path: Optional[Path] = None


@dataclasses.dataclass
class ProcessList(PyGeoApiDataClassSchema):
    processes: List[ProcessSummary] = dataclasses.field(default_factory=list)
    links: List[Link] = dataclasses.field(default_factory=list)
    schema_path: Optional[Path] = None

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

    def __init__(self):
        self.manager = ProcessManager()

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

