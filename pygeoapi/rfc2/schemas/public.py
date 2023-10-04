"""Public schemas for pygeoapi.

The schemas defined here are used for building pygeoapi core responses and can
be validated against official OGC schemas.

"""
import abc
import dataclasses
from typing import (
    Dict,
    List,
    Optional,
)


class PyGeoApiMeta(abc.ABC):
    """Additional information about an operation"""

    @abc.abstractmethod
    def as_dict(self) -> Dict:
        """Implement this method in child classes."""


class PyGeoApiSchema(abc.ABC):

    @property
    @abc.abstractmethod
    def schema_uri(self) -> Optional[str]:
        """Identifiers relevant OGC API schemas, to be used for validation.

        This should return a sequence of ids that can be used to retrieve the
        relevant jsonschema from the schema_registry.

        Implement this as a class variable or as a method in child classes.
        """

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
class Link(PyGeoApiDataClassSchema):
    href: str
    rel: Optional[str] = None
    type: Optional[str] = None
    hreflang: Optional[str] = None
    title: Optional[str] = None
    schema_uri: str = "common/part1/1.0/openapi/schemas/link.yaml"


@dataclasses.dataclass
class LandingPage(PyGeoApiDataClassSchema):
    # title is an optional element in OGC API - this demonstrates how we
    # can take an optional element and make it mandatory for pygeoapi
    title: str
    description: str
    links: List[Link] = dataclasses.field(default_factory=list)
    attribution: Optional[str] = None
    schema_uri: str = "common/part1/1.0/openapi/schemas/landingPage.yaml"

    def as_dict(self):
        result = {}
        if self.title is not None:
            result["title"] = self.title
        if self.description is not None:
            result["description"] = self.description
        if self.attribution is not None:
            result["attribution"] = self.attribution
        result["links"] = [li.as_dict() for li in self.links]
        return result


@dataclasses.dataclass
class ProcessSummary(PyGeoApiDataClassSchema):
    id: str
    version: str
    schema_uri: str = "processes-core/processSummary.yaml"


@dataclasses.dataclass
class ProcessList(PyGeoApiDataClassSchema):
    processes: List[ProcessSummary] = dataclasses.field(default_factory=list)
    links: List[Link] = dataclasses.field(default_factory=list)
    schema_uri: str = "processes/part1/1.0/openapi/schemas/processList.yaml"

    def as_dict(self) -> Dict:
        return {
            "processes": [p.as_dict() for p in self.processes],
            "links": [li.as_dict() for li in self.links]
        }
