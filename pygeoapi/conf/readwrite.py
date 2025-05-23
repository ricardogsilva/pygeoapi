"""
pygeoapi configuration management utilities allowing shared state across processes.
"""

import os
from pathlib import Path
from multiprocessing import Manager
from multiprocessing.managers import DictProxy
from typing import (
    Any,
    Iterator,
)

from pygeoapi.util import yaml_load
from pygeoapi.conf import (
    PygeoapiLoggingConfiguration,
    PygeoapiServerBindConfiguration,
)


manager = Manager()
shared_metadata_identification_config = manager.dict()
shared_metadata_license_config = manager.dict()
shared_metadata_provider_config = manager.dict()
shared_metadata_contact_config = manager.dict()
shared_server_config = manager.dict()
shared_server_map_config = manager.dict()
shared_server_process_manager_config = manager.dict()

shared_resources_config = manager.dict()



class PygeoapiSharedMetadataIdentificationConfiguration:
    title: dict[str, str]
    description: dict[str, str]
    keywords: dict[str, list[str]]
    keywords_type: str
    terms_of_service: str
    url: str

    _shared_metadata_identification: DictProxy[
        str, str | dict[str, str] | list[str]
    ]

    def __init__(
            self, shared_dict: DictProxy[
                str,
                str | list[str] | dict[str, str]
            ]
    ):
        self._shared_metadata_identification = shared_dict

    def __iter__(self) -> Iterator[str]:
        for key in self._shared_metadata_identification.keys():
            yield key

    def __getitem__(
            self,
            key: str
    ) -> (
            str | dict[str, str] | list[dict[str, str]]
    ):
        return self._shared_metadata_identification[key]

    def __getattr__(self, item: str) -> (
            str | dict[str, str] | dict[str, list[str]]
    ):
        try:
            return self._shared_metadata_identification[item]
        except KeyError:
            raise AttributeError()

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self._shared_metadata_identification.get(key)
        except KeyError:
            return default


class PygeoapiSharedMetadataLicenseConfiguration:
    name: str
    url: str

    _shared_metadata_license: DictProxy[str, str]

    def __init__(self, shared_dict: DictProxy[str, str]):
        self._shared_metadata_license = shared_dict

    def __iter__(self) -> Iterator[str]:
        for key in self._shared_metadata_license.keys():
            yield key

    def __getitem__(self, key: str) -> str:
        return self._shared_metadata_license[key]

    def __getattr__(self, item: str) -> str:
        try:
            return self._shared_metadata_license[item]
        except KeyError:
            raise AttributeError()

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self._shared_metadata_license.get(key)
        except KeyError:
            return default


class PygeoapiSharedMetadataProviderConfiguration:
    name: str
    url: str

    _shared_metadata_provider: DictProxy[str, str]

    def __init__(self, shared_dict: DictProxy[str, str]):
        self._shared_metadata_provider = shared_dict

    def __iter__(self) -> Iterator[str]:
        for key in self._shared_metadata_provider.keys():
            yield key

    def __getitem__(self, key: str) -> str:
        return self._shared_metadata_provider[key]

    def __getattr__(self, item: str) -> str:
        try:
            return self._shared_metadata_provider[item]
        except KeyError:
            raise AttributeError()

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self._shared_metadata_provider.get(key)
        except KeyError:
            return default


class PygeoapiSharedMetadataContactConfiguration:
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
    hours_of_service: str
    instructions: str
    role: str

    _shared_metadata_contact: DictProxy[str, str]

    def __init__(self, shared_dict: DictProxy[str, str]):
        self._shared_metadata_contact = shared_dict

    def __iter__(self) -> Iterator[str]:
        for key in self._shared_metadata_contact.keys():
            yield key

    def __getitem__(self, key: str) -> str:
        return self._shared_metadata_contact[key]

    def __getattr__(self, item: str) -> str:
        try:
            return self._shared_metadata_contact[item]
        except KeyError:
            raise AttributeError()

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self._shared_metadata_contact.get(key)
        except KeyError:
            return default


class PygeoapiSharedMetadataConfiguration:
    identification: PygeoapiSharedMetadataIdentificationConfiguration
    license: PygeoapiSharedMetadataLicenseConfiguration
    provider: PygeoapiSharedMetadataProviderConfiguration
    contact: PygeoapiSharedMetadataContactConfiguration

    def __init__(
            self,
            shared_identification: DictProxy[str, str | list[str] | dict[str, str]],
            shared_license: DictProxy[str, str],
            shared_provider: DictProxy[str, str],
            shared_contact: DictProxy[str, str],
    ):
        self.identification = PygeoapiSharedMetadataIdentificationConfiguration(shared_identification)
        self.license = PygeoapiSharedMetadataLicenseConfiguration(shared_license)
        self.provider = PygeoapiSharedMetadataProviderConfiguration(shared_provider)
        self.contact = PygeoapiSharedMetadataContactConfiguration(shared_contact)

    def __iter__(self) -> Iterator[str]:
        for key in self.__dict__.keys():
            yield key

    def __getitem__(self, key: str) -> (
            PygeoapiSharedMetadataIdentificationConfiguration |
            PygeoapiSharedMetadataLicenseConfiguration |
            PygeoapiSharedMetadataProviderConfiguration |
            PygeoapiSharedMetadataContactConfiguration
    ):
        try:
            return getattr(self, key)
        except AttributeError as exc:
            raise KeyError() from exc

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


class PygeoapiSharedMapConfiguration:
    url: str
    attribution: str

    _shared_map_configuration: DictProxy[str, str]

    def __init__(self, shared_dict: DictProxy[str, str]):
        self._shared_map_configuration = shared_dict

    def __iter__(self) -> Iterator[str]:
        for key in self._shared_map_configuration.keys():
            yield key

    def __getitem__(self, key: str) -> str:
        return self._shared_map_configuration[key]

    def __getattr__(self, item: str) -> str:
        try:
            return self._shared_map_configuration[item]
        except KeyError:
            raise AttributeError()

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self._shared_map_configuration.get(key)
        except KeyError:
            return default


class PygeoapiSharedProcessManagerConfiguration:
    name: str
    connection: str | None
    output_dir: str | None
    processes: dict[str, dict[str, Any]]

    _shared_process_manager_configuration: DictProxy[
        str,
        str | None | dict[str, dict[str, Any]]
    ]

    def __init__(
            self,
            shared_dict: DictProxy[
                str,
                str | dict[str, dict[str, Any]] | None
            ]
    ):
        self._shared_process_manager_configuration = shared_dict

    def __iter__(self) -> Iterator[str]:
        for key in self._shared_process_manager_configuration.keys():
            yield key

    def __getitem__(self, key: str) -> str:
        return self._shared_process_manager_configuration[key]

    def __getattr__(self, item: str) -> str:
        try:
            return self._shared_process_manager_configuration[item]
        except KeyError:
            raise AttributeError()

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self._shared_process_manager_configuration.get(key)
        except KeyError:
            return default


class PygeoapiSharedServerConfiguration:
    enable_admin: bool
    bind: PygeoapiServerBindConfiguration
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
    map: PygeoapiSharedMapConfiguration
    process_manager: PygeoapiSharedProcessManagerConfiguration | None
    ogc_schemas_location: str | None

    _shared_server_configuration: DictProxy[
        str,
        str | bool | list[str] | None
    ]

    def __init__(
            self,
            shared_server_configuration: DictProxy[
                str, str | bool | list[str] | None],
            map: PygeoapiSharedMapConfiguration,  # noqa
            process_manager: PygeoapiSharedProcessManagerConfiguration | None
    ):
        self._shared_server_configuration = shared_server_configuration
        self.map = map
        self.process_manager = process_manager

    def __iter__(self) -> Iterator[str]:
        for key in self.__dict__.keys():
            yield key

    def __getitem__(self, key: str) -> (
            PygeoapiSharedMapConfiguration |
            PygeoapiSharedProcessManagerConfiguration |
            bool | str | list[str] | None
    ):
        try:
            return getattr(self, key)
        except AttributeError as exc:
            raise KeyError() from exc

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


class PygeoapiSharedConfiguration:
    """ConfigurationManager implementation that shares state across processes.
    """

    metadata: PygeoapiSharedMetadataConfiguration
    logging: PygeoapiLoggingConfiguration
    server: PygeoapiSharedServerConfiguration
    # resources: dict[str, Any]

    def __init__(
            self,
            metadata: PygeoapiSharedMetadataConfiguration,
            logging: PygeoapiLoggingConfiguration,
            server: PygeoapiSharedServerConfiguration,
    ):
        self.metadata = metadata
        self.logging = logging
        self.server = server

    @classmethod
    def from_configuration_file(
            cls, configuration_file_path: str
    ) -> 'PygeoapiSharedConfiguration':
        if (conf_path := Path(configuration_file_path)).exists():
            with conf_path.open('r', encoding='utf-8') as fh:
                raw_conf = yaml_load(fh)

            global shared_metadata_identification_config
            global shared_metadata_license_config
            global shared_metadata_provider_config
            global shared_metadata_contact_config
            shared_metadata_identification_config.update(
                raw_conf['metadata']['identification']
            )
            shared_metadata_license_config.update(
                raw_conf['metadata']['license']
            )
            shared_metadata_provider_config.update(
                raw_conf['metadata']['provider']
            )
            shared_metadata_contact_config.update(
                raw_conf['metadata']['contact']
            )
            metadata_conf = PygeoapiSharedMetadataConfiguration(
                shared_identification=shared_metadata_identification_config,
                shared_license=shared_metadata_license_config,
                shared_provider=shared_metadata_provider_config,
                shared_contact=shared_metadata_contact_config,
            )
            global shared_server_config
            global shared_server_map_config
            global shared_server_process_manager_config
            server_conf = PygeoapiSharedServerConfiguration(
                shared_server_configuration=shared_server_config,
                map=PygeoapiSharedMapConfiguration(shared_server_map_config),
                process_manager=PygeoapiSharedProcessManagerConfiguration(
                    shared_server_process_manager_config),
            )

            return cls(
                metadata=metadata_conf,
                logging=PygeoapiLoggingConfiguration.from_dict(
                    raw_conf['logging']),
                server=server_conf,
            )
        else:
            raise RuntimeError(
                f'Configuration file {configuration_file_path} does not exist')

    @classmethod
    def from_env_variable(cls) -> 'PygeoapiSharedConfiguration':
        if (config_path := os.getenv('PYGEOAPI_CONFIG')) is not None:
            return cls.from_configuration_file(config_path)
        else:
            raise RuntimeError('PYGEOAPI_CONFIG environment variable not set')
