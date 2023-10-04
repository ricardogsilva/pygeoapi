"""Proof-of-concept (POC) for RFC2.

TODO in order to be able to demo this POC:

- Implement pygeoapi as a flask extension

- [ ] pygeoapi must drop support for Python v3.7, as the `referencing`
  third-party package being used here only supports Python 3.8+
- [ ] pygeoapi must drop the `datamodel-code-generator` dependency, as it prevents
  installation of a more recent version of `jsonschema` which is required in
  order to work with schema registries
"""
import logging

import flask
from jsonschema import Draft202012Validator
from pathlib import Path
from typing import (
    Callable,
    Optional
)

from .schemaregistry import build_schema_registry
from .schemas import public
from .process.base import get_process_manager

LOGGER = logging.getLogger(__name__)


class Api:

    def __init__(
            self,
            schemas_base_dir: Path,
    ):
        self.manager = get_process_manager()
        self.schema_registry = build_schema_registry(schemas_base_dir)

    def get_landing_page(
            self,
            url_resolver: Optional[Callable] = None
    ) -> public.LandingPage:
        response = public.LandingPage(
            title="My super duper pygeoapi POC",
            description=(
                "This is a proof of concept showing a core architecture for "
                "pygeoapi that does not depend on HTTP semantics"
            )
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
                ]
            )
        return response

    def list_processes(self, limit: Optional[int] = 100) -> public.ProcessList:
        response = public.ProcessList()
        for process_detail in self.manager.list_processes(limit=limit):
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
        schema = self.schema_registry[response.schema_uri].contents
        validator = Draft202012Validator(schema, registry=self.schema_registry)
        return validator.validate(response.as_dict())
