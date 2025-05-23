from typing import (
    Any,
    Iterator,
    Literal,
    Protocol,
    TypeAlias,
)

InternationalizationString: TypeAlias = str | dict[str, str]
InternationalizationArray: TypeAlias = list[str] | dict[str, list[str]]


class DictLikeRead(Protocol):

    def __iter__(self) -> Iterator[str]:
        ...

    def __getitem__(
            self,
            key: str
    ) -> Any:
        """Retrieve a configuration value using a dict-like interface."""

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value or the default value."""


class DictLikeWrite(Protocol):

    def __setitem__(self, key: Literal['processes'], value: Any) -> None:
        """Assign a configuration value using a dict-like interface.

        Compatibility note: This method exists in order to allow the
        `pygeoapi.process.manager.get_manager()` function to mutate the
        process manager configuration, specifically to allow it to provide
        process definitions to it.
        """


class LinkConfiguration(DictLikeRead, Protocol):
    type: str
    rel: str
    href: str
    title: str | None
    hreflang: str | None
    length: str | None


class MetadataIdentificationConfiguration(DictLikeRead, Protocol):
    title: InternationalizationString
    description: InternationalizationString
    keywords: InternationalizationArray
    keywords_type: Literal['discipline', 'temporal', 'place', 'theme', 'stratum'] | None
    terms_of_service: InternationalizationString
    url: str


class MetadataLicenseConfiguration(DictLikeRead, Protocol):
    name: InternationalizationString
    url: InternationalizationString | None


class MetadataProviderConfiguration(DictLikeRead, Protocol):
    name: InternationalizationString
    url: InternationalizationString | None


class MetadataContactConfiguration(DictLikeRead, Protocol):
    name: str
    position: str | None
    address: str | None
    city: str | None
    state_or_province: str | None
    postal_code: str | None
    country: str | None
    phone: str | None
    fax: str | None
    email: str | None
    url: str | None
    hours: str | None
    instructions: str | None
    role: str | None


class MetadataConfiguration(DictLikeRead, Protocol):
    identification: MetadataIdentificationConfiguration
    license: MetadataLicenseConfiguration
    provider: MetadataProviderConfiguration
    contact: MetadataContactConfiguration


class ProcessManagerConfiguration(DictLikeRead, DictLikeWrite, Protocol):
    name: str
    connection: str
    output_dir: str
    processes: dict[str, dict[str, Any]]


class MapConfiguration(DictLikeRead, Protocol):
    url: str
    attribution: str


class ServerConfiguration(DictLikeRead, Protocol):
    enable_admin: bool
    public_url: str
    mimetype: str
    encoding: str
    languages: list[str]
    pretty_print_responses: bool
    limit: int
    templates_path: str
    static_path: str
    map: MapConfiguration
    process_manager: ProcessManagerConfiguration | None
    ogc_schemas_location: str | None


class ProcessorConfiguration(Protocol):
    name: str


class ProcessResourceConfiguration(Protocol):
    type: Literal['process']
    processor: ProcessorConfiguration


class CollectionProviderFeatureConfiguration(Protocol):
    type: Literal['feature']


class CollectionProviderCoverageConfiguration(Protocol):
    type: Literal['coverage']


class CollectionProviderTileConfiguration(Protocol):
    type: Literal['tile']


class CollectionResourceSpatialExtentConfiguration(Protocol):
    bbox: tuple[float, float, float, float] | tuple[float, float, float, float, float, float]
    crs: str | None


class CollectionResourceTemporalExtentConfiguration(Protocol):
    begin: str | None
    end: str | None
    trs: str | None


class CollectionResourceExtentConfiguration(Protocol):
    spatial: CollectionResourceSpatialExtentConfiguration
    temporal: CollectionResourceTemporalExtentConfiguration


class LimitsConfiguration(Protocol):
    max_items: int
    default_items: int
    max_distance_x: float
    max_distance_y: float
    max_distance_units: float
    on_exceed: Literal['error', 'throttle']


class CollectionResourceConfiguration(Protocol):
    type: Literal['collection']
    title: InternationalizationString
    description: InternationalizationString
    keywords: InternationalizationArray
    extents: CollectionResourceExtentConfiguration
    providers: list[
        CollectionProviderFeatureConfiguration |
        CollectionProviderCoverageConfiguration |
        CollectionProviderTileConfiguration
    ]
    visibility: Literal['default', 'hidden'] | None = 'default'
    linked_data: dict[str, Any] | None
    links: list[LinkConfiguration] | None
    limits: LimitsConfiguration | None


class StacCollectionResourceConfiguration(Protocol):
    type: Literal['stac-collection']


class ConfigurationManager(DictLikeRead, Protocol):
    """Protocol that pygeoapi relies upon for configuration management."""
    # Implementation notes:
    #
    # Support for these properties that used to exist under the `server`
    # section has been removed:
    #
    # - `server.bind`
    # - `server.gzip`
    # - `server.cors`
    #
    # All of these are configuration properties suitable for the web
    # application server (e.g. gunicorn, uvicorn, etc) that pygeoapi is
    # being wrapped with, but they are not relevant to pygeoapi.
    #
    # Additionally, support for the `logging` property has also been removed.
    # This is a configuration property suitable for either the web application
    # framework (e.g.flask, starlette, etc) or the web server, but it is not
    # relevant to pygeoapi.

    metadata: MetadataConfiguration
    server: ServerConfiguration
    resources: dict[
        str,
        CollectionResourceConfiguration |
        StacCollectionResourceConfiguration |
        ProcessResourceConfiguration
    ]

    def as_dict(self) -> dict[str, dict[str, Any]]:
        """Return a dict representation of the configuration."""
        ...
