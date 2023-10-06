"""Internal schemas used by pygeoapi.

The schemas defined here are used by pygeoapi internals and are not exposed
to the world. Therefore, these are free to hold any application-specific
data.

"""
import dataclasses
from typing import (
    List,
    Optional,
)


@dataclasses.dataclass
class PyGeoApiMetadataIdentificationConfig:
    title: str
    description: str
    keywords: List[str]
    keywords_type: str
    terms_of_service: str
    url: str


@dataclasses.dataclass
class PyGeoApiMetadataLicenseConfig:
    name: str
    url: str


@dataclasses.dataclass
class PyGeoApiMetadataProviderConfig:
    name: str
    url: str


@dataclasses.dataclass
class PyGeoApiMetadataPointOfContactConfig:
    name: str
    position: str
    address: str
    city: str
    state_or_province: str
    postal_code: str
    country: str
    phone: str
    fax: str
    email: str
    url: str
    hours: str
    instructions: str
    role: str


@dataclasses.dataclass
class PyGeoApiMetadataConfig:
    identification: PyGeoApiMetadataIdentificationConfig
    license: PyGeoApiMetadataLicenseConfig
    provider: PyGeoApiMetadataProviderConfig
    point_of_contact: PyGeoApiMetadataPointOfContactConfig


@dataclasses.dataclass
class PyGeoApiConfig:
    debug: bool
    language: str
    metadata: PyGeoApiMetadataConfig
    ogc_api_schemas_base_dir: Optional[str]
    pagination_limit: int
    validate_responses: bool


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
