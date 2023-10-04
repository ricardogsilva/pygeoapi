"""Utilities for creating a schema registry of official OGC schemas."""
import logging
from pathlib import Path
from typing import (
    Dict,
    Optional,
)

import referencing.jsonschema
import yaml
from referencing import (
    Registry,
    Resource,
)

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
        if child.is_file() and child.suffix in (".yaml", ".json") and child.parent.name == "schemas":
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
