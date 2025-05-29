"""
pygeoapi configuration management utilities allowing shared state across processes.
"""

import logging
import os
from pathlib import Path
from multiprocessing import Manager
from multiprocessing.managers import DictProxy
from typing import (
    Any,
    Iterator,
    Union,
)

from pygeoapi.util import yaml_load
from pygeoapi.conf.defaults import (
    DEFAULT_ENCODING,
    DEFAULT_STATIC_PATH,
    DEFAULT_TEMPLATES_PATH,
    DEFAULT_MEDIA_TYPE
)
from pygeoapi.conf.readonly import (
    DictLikeRead,
    parse_resource_configuration,
    PygeoapiCollectionResourceConfiguration,
    PygeoapiProcessResourceConfiguration,
    PygeoapiServerConfiguration,
)

LOGGER = logging.getLogger(__name__)
multiproccessing_manager = Manager()
shared_metadata_identification_config = multiproccessing_manager.dict()
shared_metadata_license_config = multiproccessing_manager.dict()
shared_metadata_provider_config = multiproccessing_manager.dict()
shared_metadata_contact_config = multiproccessing_manager.dict()
shared_server_config = multiproccessing_manager.dict()
shared_server_map_config = multiproccessing_manager.dict()
shared_server_process_manager_config = multiproccessing_manager.dict()
shared_resources_config = multiproccessing_manager.dict()


class SharedAttributeRead:
    _shared_state: DictProxy

    def __getattr__(self, item: str) -> (
            str | dict[str, str | dict[str, str | list[str]]]
    ):
        try:
            return self._shared_state[item]
        except KeyError:
            raise AttributeError()

    def __dir__(self):
        # This method is useful for being able to have autocomplete in the
        # Python REPL
        normal_attrs = object.__dir__(self)
        annotated_attrs = list(self.__annotations__.keys())
        return list(set(normal_attrs + annotated_attrs))


class SharedDictLikeRead:
    _shared_state: DictProxy

    # provide also a __contains__ implementation

    def __iter__(self) -> Iterator[str]:
        for key in self.__dict__.keys():
            yield key

    def __getitem__(
            self,
            key: str
    ) -> (
            str | dict[str, str] | list[dict[str, str]]
    ):
        try:
            return getattr(self, key)
        except AttributeError as exc:
            raise KeyError() from exc

    def __contains__(self, item: str) -> bool:
        return item in self._shared_state

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self._shared_state.get(key)
        except KeyError:
            return default

    def as_dict(self) -> dict:
        return dict(self._shared_state)


class SharedStateUpdateMixin:
    _shared_state: DictProxy

    def update(self, data: dict[str, Any]) -> None:
        self._shared_state.update(data)


class PygeoapiSharedMetadataIdentificationConfiguration(
    SharedDictLikeRead, SharedAttributeRead, SharedStateUpdateMixin
):
    title: dict[str, str]
    description: dict[str, str]
    keywords: dict[str, list[str]]
    keywords_type: str
    terms_of_service: str
    url: str

    _shared_state: DictProxy

    def __init__(
            self, shared_dict: DictProxy
    ):
        self._shared_state = shared_dict


class PygeoapiSharedMetadataLicenseConfiguration(
    SharedDictLikeRead,
    SharedAttributeRead,
    SharedStateUpdateMixin,
):
    name: str
    url: str

    def __init__(self, shared_dict: DictProxy):
        self._shared_state = shared_dict


class PygeoapiSharedMetadataProviderConfiguration(
    SharedDictLikeRead,
    SharedAttributeRead,
    SharedStateUpdateMixin,
):
    name: str
    url: str

    def __init__(self, shared_dict: DictProxy):
        self._shared_state = shared_dict


class PygeoapiSharedMetadataContactConfiguration(
    SharedDictLikeRead,
    SharedAttributeRead,
    SharedStateUpdateMixin,
):
    name: str
    position: str
    address: str
    city: str
    stateorprovince: str
    postalcode: str
    country: str
    phone: str
    fax: str
    email: str
    url: str
    hours: str
    instructions: str
    role: str

    _shared_state: DictProxy

    def __init__(self, shared_dict: DictProxy):
        self._shared_state = shared_dict


class PygeoapiSharedMetadataConfiguration(DictLikeRead):
    identification: PygeoapiSharedMetadataIdentificationConfiguration
    license: PygeoapiSharedMetadataLicenseConfiguration
    provider: PygeoapiSharedMetadataProviderConfiguration
    contact: PygeoapiSharedMetadataContactConfiguration

    def __init__(
            self,
            shared_identification: DictProxy,
            shared_license: DictProxy,
            shared_provider: DictProxy,
            shared_contact: DictProxy,
    ):
        self.identification = PygeoapiSharedMetadataIdentificationConfiguration(
            shared_identification)
        self.license = PygeoapiSharedMetadataLicenseConfiguration(
            shared_license)
        self.provider = PygeoapiSharedMetadataProviderConfiguration(
            shared_provider)
        self.contact = PygeoapiSharedMetadataContactConfiguration(
            shared_contact)

    def as_dict(self) -> dict:
        return {
            'identification': self.identification.as_dict(),
            'license': self.license.as_dict(),
            'provider': self.provider.as_dict(),
            'contact': self.contact.as_dict(),
        }

    def update(self, data: dict[str, Any]) -> None:
        for key, value in data.items():
            if (attribute := getattr(self, key, None)) is not None:
                attribute.update(value)


class PygeoapiSharedMapConfiguration(
    SharedDictLikeRead,
    SharedAttributeRead,
    SharedStateUpdateMixin,
):
    url: str
    attribution: str

    _shared_state: DictProxy

    def __init__(self, shared_dict: DictProxy):
        self._shared_state = shared_dict


class PygeoapiSharedProcessesConfiguration(SharedStateUpdateMixin):
    _shared_state: DictProxy

    def __init__(self, shared_resources_configuration: DictProxy):
        # shared state is really all resources, but we operate only on the processes
        self._shared_state = shared_resources_configuration

    def __iter__(self) -> Iterator[str]:
        for key, value in self._shared_state.items():
            if value['type'] == 'process':
                yield key

    def __getitem__(
            self,
            key: str
    ) -> PygeoapiProcessResourceConfiguration:
        raw_resource = self._shared_state[key]
        if raw_resource['type'] == 'process':
            return parse_resource_configuration(key, raw_resource)
        else:
            raise KeyError()

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def items(self) -> Iterator[
        tuple[
            str,
            PygeoapiProcessResourceConfiguration
        ]
    ]:
        for k, v in self._shared_state.items():
            if v['type'] == 'process':
                yield k, parse_resource_configuration(k, v)

    def keys(self) -> Iterator[str]:
        for k, v in self._shared_state.items():
            if v['type'] == 'process':
                yield k

    def values(self) -> Iterator[PygeoapiProcessResourceConfiguration]:
        for k, v in self._shared_state.items():
            if v['type'] == 'process':
                yield parse_resource_configuration(k, v)

    def as_dict(self) -> dict[str, dict[str, Any]]:
        return {
            k: v for k, v in self._shared_state.items() if v['type'] == 'process'
        }


class PygeoapiSharedProcessManagerConfiguration(
    SharedDictLikeRead, SharedAttributeRead
):
    name: str
    connection: str | None
    output_dir: str | None
    processes: PygeoapiSharedProcessesConfiguration

    _shared_state: DictProxy

    def __init__(
            self,
            shared_dict: DictProxy,
            shared_resources_dict: DictProxy
    ):
        self._shared_state = shared_dict
        self.processes = PygeoapiSharedProcessesConfiguration(
            shared_resources_dict)

    def get(self, key: str, default: Any = None) -> Any:
        if key == 'processes':
            return self.processes
        else:
            return super().get(key, default)

    def as_dict(self) -> dict:
        result = super().as_dict()
        result['processes'] = self.processes.as_dict()
        return result

    def update(self, data: dict[str, Any]) -> None:
        for key, value in data.items():
            if key == 'processes':
                self.processes.update(value)
            else:
                self._shared_state[key] = value


class PygeoapiSharedServerConfiguration(
    SharedDictLikeRead,
    SharedAttributeRead,
):
    admin: bool
    url: str
    mimetype: str
    encoding: str
    languages: list[str]
    pretty_print: bool
    limit: int
    templates_path: str
    static_path: str
    map: PygeoapiSharedMapConfiguration
    manager: PygeoapiSharedProcessManagerConfiguration | None
    ogc_schemas_location: str | None

    _shared_state: DictProxy

    def __init__(
            self,
            shared_server_configuration: DictProxy,
            map: PygeoapiSharedMapConfiguration,  # noqa
            process_manager: PygeoapiSharedProcessManagerConfiguration | None
    ):
        self._shared_state = shared_server_configuration
        self.map = map
        self.manager = process_manager

    def __getattr__(self, item: str):
        if item == 'templates_path':
            result = self._shared_state['templates'].get('path')
        elif item == 'static_path':
            result = self._shared_state['templates'].get('static')
        else:
            result = super().__getattr__(item)
        return result

    def as_dict(self) -> dict:
        result = super().as_dict()
        result.update({
            'map': self.map.as_dict(),
            'manager': self.manager.as_dict(),
        })
        return result

    def update(self, data: dict[str, Any]) -> None:
        for key, value in data.items():
            if key in ('map', 'manager'):
                getattr(self, key).update(value)
            else:
                self._shared_state[key] = value


class PygeoapiSharedResourcesConfiguration(SharedStateUpdateMixin):
    _shared_state: DictProxy

    def __init__(self, shared_resources_configuration: DictProxy):
        self._shared_state = shared_resources_configuration

    def __iter__(self) -> Iterator[str]:
        for key in self._shared_state.keys():
            yield key

    def __getitem__(
            self,
            key: str
    ) -> Union[
        PygeoapiCollectionResourceConfiguration,
        PygeoapiProcessResourceConfiguration
    ]:
        raw_resource = self._shared_state[key]
        return parse_resource_configuration(key, raw_resource)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def items(self) -> Iterator[
        tuple[
            str,
            Union[
                PygeoapiCollectionResourceConfiguration,
                PygeoapiProcessResourceConfiguration
            ]
        ]
    ]:
        for k, v in self._shared_state.items():
            yield k, parse_resource_configuration(k, v)

    def keys(self) -> Iterator[str]:
        for k in self._shared_state.keys():
            yield k

    def values(self) -> Iterator[
        PygeoapiCollectionResourceConfiguration |
        PygeoapiProcessResourceConfiguration
        ]:
        for k, v in self._shared_state.items():
            yield parse_resource_configuration(k, v)

    def as_dict(self) -> dict[str, dict[str, Any]]:
        return {
            k: v for k, v in self._shared_state.items()
        }


class PygeoapiSharedConfiguration(DictLikeRead):
    """ConfigurationManager implementation that shares state across processes.
    """

    metadata: PygeoapiSharedMetadataConfiguration
    server: PygeoapiSharedServerConfiguration
    resources: PygeoapiSharedResourcesConfiguration

    def __init__(
            self,
            metadata: PygeoapiSharedMetadataConfiguration,
            server: PygeoapiSharedServerConfiguration,
            resources: PygeoapiSharedResourcesConfiguration
    ):
        self.metadata = metadata
        self.server = server
        self.resources = resources

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        global shared_metadata_identification_config
        shared_metadata_identification_config.update(
            data['metadata']['identification']
        )

        global shared_metadata_license_config
        shared_metadata_license_config.update(
            data['metadata']['license']
        )

        global shared_metadata_provider_config
        shared_metadata_provider_config.update(
            data['metadata']['provider']
        )

        global shared_metadata_contact_config
        shared_metadata_contact_config.update(
            data['metadata']['contact']
        )

        global shared_server_config
        shared_server_config.update(data['server'])
        if shared_server_config.get('mimetype') is None:
            shared_server_config['mimetype'] = DEFAULT_MEDIA_TYPE
        if shared_server_config.get('encoding') is None:
            shared_server_config['encoding'] = DEFAULT_ENCODING
        if (shared_server_config.get('templates', {}).get('path')) is None:
            templates_dict = shared_server_config.setdefault('templates', {})
            templates_dict['path'] = DEFAULT_TEMPLATES_PATH
            shared_server_config['templates'] = templates_dict
        if (shared_server_config.get('templates', {}).get('static')) is None:
            templates_dict = shared_server_config.setdefault('templates', {})
            templates_dict['static'] = DEFAULT_STATIC_PATH
            shared_server_config['templates'] = templates_dict

        del shared_server_config['map']
        del shared_server_config['manager']

        global shared_server_map_config
        shared_server_map_config.update(data['server']['map'])

        global shared_server_process_manager_config
        shared_server_process_manager_config.update(
            data['server'].get('manager', {}))

        global shared_resources_config
        shared_resources_config.update(data['resources'])

        return cls(
            metadata=PygeoapiSharedMetadataConfiguration(
                shared_identification=shared_metadata_identification_config,
                shared_license=shared_metadata_license_config,
                shared_provider=shared_metadata_provider_config,
                shared_contact=shared_metadata_contact_config,
            ),
            server=PygeoapiSharedServerConfiguration(
                shared_server_configuration=shared_server_config,
                map=PygeoapiSharedMapConfiguration(shared_server_map_config),
                process_manager=PygeoapiSharedProcessManagerConfiguration(
                    shared_server_process_manager_config,
                    shared_resources_config
                ),
            ),
            resources=PygeoapiSharedResourcesConfiguration(shared_resources_config)
        )

    @classmethod
    def from_configuration_file(
            cls, configuration_file_path: str
    ) -> 'PygeoapiSharedConfiguration':
        if (conf_path := Path(configuration_file_path)).exists():
            with conf_path.open('r', encoding='utf-8') as fh:
                raw_conf = yaml_load(fh)
                return cls.from_dict(raw_conf)
        else:
            raise RuntimeError(
                f'Configuration file {configuration_file_path} does not exist')

    @classmethod
    def from_env_variable(cls) -> 'PygeoapiSharedConfiguration':
        if (config_path := os.getenv('PYGEOAPI_CONFIG')) is not None:
            return cls.from_configuration_file(config_path)
        else:
            raise RuntimeError('PYGEOAPI_CONFIG environment variable not set')

    def as_dict(self) -> dict:
        return {
            'metadata': self.metadata.as_dict(),
            'server': self.server.as_dict(),
            'resources': self.resources.as_dict()
        }

    def update(self, data: dict[str, Any]) -> None:
        for key, value in data.items():
            if (attribute := getattr(self, key)) is not None:
                attribute.update(value)
            else:
                raise RuntimeError(f'Attribute {key!r} not found')
