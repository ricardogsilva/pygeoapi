from typing import (
    Any,
    Iterator,
    Literal,
    Protocol,
)


class MetadataIdentificationConfiguration(Protocol):
    title: dict[str, str]
    description: dict[str, str]
    keywords: dict[str, list[str]]
    keywords_type: str
    terms_of_service: str
    url: str

    def __getitem__(
            self,
            key: str
    ) -> (
            str | dict[str, str] | list[dict[str, str]]
    ):
        """Retrieve a configuration value using a dict-like interface."""
        ...

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value or the default value."""
        ...


class MetadataLicenseConfiguration(Protocol):
    name: str
    url: str

    def __getitem__(self, key: str) -> str:
        """Retrieve a configuration value using a dict-like interface."""
        ...

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value or the default value."""
        ...


class MetadataProviderConfiguration(Protocol):
    name: str
    url: str

    def __getitem__(self, key: str) -> str:
        """Retrieve a configuration value using a dict-like interface."""
        ...

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value or the default value."""
        ...


class MetadataContactConfiguration(Protocol):
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

    def __getitem__(self, key: str) -> str:
        """Retrieve a configuration value using a dict-like interface."""
        ...

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value or the default value."""
        ...


class MetadataConfiguration(Protocol):
    identification: MetadataIdentificationConfiguration
    license: MetadataLicenseConfiguration
    provider: MetadataProviderConfiguration
    contact: MetadataContactConfiguration

    def __getitem__(
            self,
            key: str
    ) -> (
            MetadataIdentificationConfiguration |
            MetadataLicenseConfiguration |
            MetadataProviderConfiguration |
            MetadataContactConfiguration
    ):
        """Retrieve a configuration value using a dict-like interface."""
        ...

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value or the default value."""
        ...


class LoggingConfiguration(Protocol):
    level: str

    def __getitem__(self, key: str) -> str:
        """Retrieve a configuration value using a dict-like interface."""
        ...

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value or the default value."""
        ...


class ProcessManagerConfiguration(Protocol):
    name: str
    connection: str
    output_dir: str
    processes: dict[str, dict[str, Any]]

    def __getitem__(self, key: str) -> str:
        """Retrieve a configuration value using a dict-like interface."""
        ...

    def __setitem__(self, key: Literal['processes'], value: Any) -> None:
        """Assign a configuration value using a dict-like interface.

        Compatibility note: This method exists in order to allow the
        `pygeoapi.process.manager.get_manager()` function to mutate the
        process manager configuration, specifically to allow it to provide
        process definitions to it.
        """

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value or the default value."""
        ...


class MapConfiguration(Protocol):
    url: str
    attribution: str

    def __getitem__(self, key: str) -> str:
        """Retrieve a configuration value using a dict-like interface."""
        ...

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value or the default value."""
        ...


class ServerBindConfiguration(Protocol):
    host: str
    port: int

    def __getitem__(self, key: str) -> str | int:
        """Retrieve a configuration value using a dict-like interface."""
        ...

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value or the default value."""
        ...


class ServerConfiguration(Protocol):
    enable_admin: bool
    bind: ServerBindConfiguration
    public_url: str
    mimetype: str
    encoding: str
    gzip_responses: bool
    languages: list[str]
    enable_cors: bool
    pretty_print_responses: bool
    limit: int
    templates_path: str
    static_path: str
    map: MapConfiguration
    process_manager: ProcessManagerConfiguration | None
    ogc_schemas_location: str | None

    def __getitem__(
            self,
            key: str
    ) -> (
            bool | int | str | list[str] | None |
            ProcessManagerConfiguration | ServerBindConfiguration
        ):
        """Retrieve a configuration value using a dict-like interface."""
        ...

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value or the default value."""
        ...


class ConfigurationManager(Protocol):
    """Protocol that pygeoapi relies upon for configuration management."""
    metadata: MetadataConfiguration
    logging: LoggingConfiguration
    server: ServerConfiguration
    resources: dict[str, Any]

    def __iter__(self) -> Iterator[str]:
        ...

    def __getitem__(
            self,
            key: str
    ) -> (
            MetadataConfiguration |
            LoggingConfiguration |
            ServerConfiguration |
            dict[str, Any]
    ):
        """Retrieve a configuration value using a dict-like interface."""
        ...

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value or the default value."""
        ...

    def as_dict(self) -> dict[str, dict[str, Any]]:
        """Return a dict representation of the configuration."""
        ...
