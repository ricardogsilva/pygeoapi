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

    def items(self) -> Iterator[tuple[str, Any]]:
        """Retrieve matching combinations of key-value pairs"""
        ...

    def keys(self) -> Iterator[str]:
        ...

    def values(self) -> Iterator[Any]:
        ...



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
    length: int


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
    stateorprovince: str | None
    postalcode: str | None
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


class ProcessesConfiguration(DictLikeRead, Protocol):
    """Contains a set of process resources and has a dict-like interface"""


class ProcessManagerConfiguration(DictLikeRead, Protocol):
    identifier: str
    connection: str
    output_dir: str
    processes: ProcessesConfiguration


class MapConfiguration(DictLikeRead, Protocol):
    url: str
    attribution: str


class ServerConfiguration(DictLikeRead, Protocol):
    admin: bool
    url: str
    mimetype: str
    encoding: str
    languages: list[str]
    pretty_print: bool
    limit: int
    templates_path: str
    static_path: str
    map: MapConfiguration
    manager: ProcessManagerConfiguration | None
    ogc_schemas_location: str | None


class ProcessorConfiguration(Protocol):
    name: str


class ProcessResourceConfiguration(Protocol):
    name: str
    type: Literal['process']
    processor: ProcessorConfiguration


class CollectionProviderGeometryConfiguration(DictLikeRead, Protocol):
    x_field: str
    y_field: str


class CollectionProviderMediaTypeConfiguration(DictLikeRead, Protocol):
    name: str
    mimetype: str


class CollectionProviderConfiguration(DictLikeRead, Protocol):
    type: Literal[
        'coverage',
        'edr',
        'feature',
        'map',
        'record',
        'stac',
        'tile',
    ]
    name: str
    data: str | dict[str, Any]
    default: bool
    editable: bool
    table: str | None
    id_field: str | None
    geometry: CollectionProviderGeometryConfiguration | None
    time_field: str | None
    title_field: str | None
    format: CollectionProviderMediaTypeConfiguration | None
    options: dict[str, Any] | None
    properties: list[str] | None
    crs: list[str]
    storage_crs: str
    storage_crs_coordinate_epoch: str | None


class CollectionResourceSpatialExtentConfiguration(Protocol):
    bbox: tuple[float, float, float, float] | tuple[float, float, float, float, float, float]
    crs: str


class CollectionResourceTemporalExtentConfiguration(Protocol):
    begin: str | None
    end: str | None
    trs: str | None


class CollectionResourceExtentsConfiguration(Protocol):
    spatial: CollectionResourceSpatialExtentConfiguration
    temporal: CollectionResourceTemporalExtentConfiguration | None


class LimitsConfiguration(Protocol):
    max_items: int
    default_items: int
    max_distance_x: float
    max_distance_y: float
    max_distance_units: str
    on_exceed: Literal['error', 'throttle']


class CollectionResourceConfiguration(DictLikeRead, Protocol):
    identifier: str
    type: Literal[
        'collection',
        'stac-collection',
    ]
    visibility: Literal['default', 'hidden'] | None
    title: InternationalizationString
    description: InternationalizationString
    keywords: InternationalizationArray
    linked_data: dict[str, str | dict] | None
    links: list[LinkConfiguration] | None
    extents: CollectionResourceExtentsConfiguration
    limits: LimitsConfiguration | None
    providers: list[CollectionProviderConfiguration]


class ResourcesConfiguration(DictLikeRead, Protocol):
    """Contains a set of resources and has a dict-like interface"""


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
    resources: ResourcesConfiguration

    def as_dict(self) -> dict[str, dict[str, Any]]:
        """Return a dict representation of the configuration."""
        ...


class ConfigurationInitializer(Protocol):

    def __call__(self) -> ConfigurationManager:
        """Return an object which implements the pygeoapi configuration interface."""
