"""Proof-of-concept (POC) for RFC2.

TODO in order to be able to demo this POC:

- Implement pygeoapi as a flask extension

- [ ] pygeoapi must drop support for Python v3.7, as the `referencing`
  third-party package being used here only supports Python 3.8+
- [ ] pygeoapi must drop the `datamodel-code-generator` dependency, as it prevents
  installation of a more recent version of `jsonschema` which is required in
  order to work with schema registries
"""
import dataclasses
import logging

from jsonschema import Draft202012Validator
from pathlib import Path
from referencing import Registry
from typing import (
    Callable,
    Dict,
    List,
    Optional,
)

from . import config
from .schemaregistry import build_schema_registry
from .schemas import (
    internal,
    public,
)
from .process.base import (
    PyGeoApiProcessManager,
    get_process_manager,
)

LOGGER = logging.getLogger(__name__)


class Api:
    identification: internal.PyGeoApiMetadataIdentificationConfig
    point_of_contact: internal.PyGeoApiMetadataPointOfContactConfig
    license: internal.PyGeoApiMetadataLicenseConfig
    provider: internal.PyGeoApiMetadataProviderConfig
    process_manager: PyGeoApiProcessManager
    schema_registry: Optional[Registry]
    default_pagination_limit: int
    conformance_classes: Dict[str, List[str]] = {
        "ogcapi-features": [],
        "ogcapi-processes": [
            "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/core",
            "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/ogc-process-description",
            "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/json",
            "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/job-list",
            "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/callback",
            "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/dismiss",
        ],
    }

    def __init__(
            self,
            schemas_base_dir: Path,
            default_pagination_limit: int,
            process_manager: PyGeoApiProcessManager,
            identification: internal.PyGeoApiMetadataIdentificationConfig,
            point_of_contact: internal.PyGeoApiMetadataPointOfContactConfig,
            license: internal.PyGeoApiMetadataLicenseConfig,
            provider: internal.PyGeoApiMetadataProviderConfig,
    ):
        self.identification = internal.PyGeoApiMetadataIdentificationConfig(
            **dataclasses.asdict(identification))
        self.point_of_contact = internal.PyGeoApiMetadataPointOfContactConfig(
            **dataclasses.asdict(point_of_contact)
        )
        self.license = internal.PyGeoApiMetadataLicenseConfig(
            **dataclasses.asdict(license))
        self.provider = internal.PyGeoApiMetadataProviderConfig(
            **dataclasses.asdict(provider))
        self.default_pagination_limit = default_pagination_limit
        self.process_manager = process_manager
        try:
            self.schema_registry = build_schema_registry(schemas_base_dir)
        except FileNotFoundError as err:
            LOGGER.warning(
                "Could not build schema registry, schema validation disabled")
            LOGGER.debug(err)
            self.schema_registry = None

    def get_landing_page(
            self,
            url_resolver: Optional[Callable] = None
    ) -> public.LandingPage:
        response = public.LandingPage(
            title=self.identification.title,
            description=self.identification.description,
        )
        if url_resolver is not None:
            response.links.extend(
                [
                    public.Link(
                        href=url_resolver(self.get_landing_page),
                        rel="self",
                        title="This document as JSON",
                        type="application/json"
                    ),
                    public.Link(
                        href=url_resolver(self.get_landing_page),
                        rel="self",
                        title="This document as HTML",
                        type="text/html"
                    ),
                    public.Link(
                        href=url_resolver(self.get_conformance),
                        rel="http://www.opengis.net/def/rel/ogc/1.0/conformance",
                        title="Conformance",
                        type="application/json"
                    ),
                    public.Link(
                        href=url_resolver(self.get_conformance),
                        rel="conformance",
                        title="Conformance as HTML",
                        type="text/html"
                    ),
                    public.Link(
                        href=url_resolver(self.list_processes),
                        rel="http://www.opengis.net/def/rel/ogc/1.0/processes",
                        title="List of processes as JSON",
                        type="application/json",
                    ),
                    public.Link(
                        href=url_resolver(self.list_processes),
                        rel="http://www.opengis.net/def/rel/ogc/1.0/processes",
                        title="List of processes as HTML",
                        type="text/html",
                    ),
                ]
            )
        return response

    def get_conformance(self) -> public.Conformance:
        result = public.Conformance()
        for spec, conformance_classes in self.conformance_classes.items():
            result.conformsTo.extend(conformance_classes)
        return result

    def get_api_definition(self):
        ...

    def get_api_docs(self):
        ...

    def list_processes(self, limit: Optional[int] = None) -> public.ProcessList:
        response = public.ProcessList()
        for process_detail in self.process_manager.list_processes(
                limit=limit or self.default_pagination_limit):
            summary = public.ProcessSummary(
                id=process_detail.id,
                version="0.1.0"
            )
            response.processes.append(summary)
        response.links.extend(
            [
                public.Link(href="some-relevant-url", rel="self"),
                public.Link(
                    href="some-relevant-url",
                    rel="alternate",
                    title="This document as HTML"
                ),
            ]
        )
        return response

    def validate(self, response: public.PyGeoApiSchema):
        if self.schema_registry is not None:
            schema = self.schema_registry[response.schema_uri].contents
            validator = Draft202012Validator(
                schema, registry=self.schema_registry)
            validator.validate(response.as_dict())
        else:
            LOGGER.warning(
                "No schema registry is available, skipping validation...")


def get_api(pygeoapi_config: Optional[internal.PyGeoApiConfig] = None) -> Api:
    pygeoapi_config = pygeoapi_config or config.get_config()
    return Api(
        identification=pygeoapi_config.metadata.identification,
        point_of_contact=pygeoapi_config.metadata.point_of_contact,
        license=pygeoapi_config.metadata.license,
        provider=pygeoapi_config.metadata.provider,
        default_pagination_limit=pygeoapi_config.pagination_limit,
        schemas_base_dir=Path(pygeoapi_config.ogc_api_schemas_base_dir),
        process_manager=get_process_manager(),
    )
