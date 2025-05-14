"""pygeoapi configuration management utilities."""

import dataclasses
from pathlib import Path
from typing import (
    Any,
    Iterator,
    Literal,
)

from pygeoapi.util import yaml_load


@dataclasses.dataclass
class PygeoapiMetadataIdentificationConfiguration:
    """Implements the `MetadataIdentificationConfiguration` protocol"""
    title: dict[str, str]
    description: dict[str, str]
    keywords: dict[str, list[str]]
    keywords_type: str
    terms_of_service: str
    url: str

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

    @classmethod
    def from_dict(
            cls,
            values: dict[
                str,
                str | list[str] | dict[str, str]
            ],
            default_language_code: str = 'en',
    ) -> 'PygeoapiMetadataIdentificationConfiguration':
        if isinstance(raw_keywords := values.get('keywords'), dict):
            parsed_keywords = {k: v for k, v in raw_keywords.items()}
        else:
            parsed_keywords = {default_language_code: raw_keywords}
        return cls(
            title=_parse_multilingual_string(
                values['title'],
                default_language_code
            ),
            description=_parse_multilingual_string(
                values.get('description', ''),
                default_language_code
            ),
            keywords=parsed_keywords,
            keywords_type=values.get('keywords_type', ''),
            terms_of_service=values.get('terms_of_service'),
            url=values.get('url', ''),
        )

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


@dataclasses.dataclass
class PygeoapiMetadataLicenseConfiguration:
    name: str
    url: str

    def __iter__(self) -> Iterator[str]:
        for key in self.__dict__.keys():
            yield key

    def __getitem__(self, key: str) -> str:
        try:
            return getattr(self, key)
        except AttributeError as exc:
            raise KeyError() from exc

    @classmethod
    def from_dict(
            cls, values: dict[str, str]) -> 'PygeoapiMetadataLicenseConfiguration':
        return cls(
            name=values['name'],
            url=values.get('url'),
        )

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


@dataclasses.dataclass
class PygeoapiMetadataProviderConfiguration:
    name: str
    url: str

    def __iter__(self) -> Iterator[str]:
        for key in self.__dict__.keys():
            yield key

    def __getitem__(self, key: str) -> str:
        try:
            return getattr(self, key)
        except AttributeError as exc:
            raise KeyError() from exc

    @classmethod
    def from_dict(
            cls, values: dict[str, str]) -> 'PygeoapiMetadataProviderConfiguration':
        return cls(
            name=values['name'],
            url=values.get('url'),
        )

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


@dataclasses.dataclass
class PygeoapiMetadataContactConfiguration:
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

    def __iter__(self) -> Iterator[str]:
        for key in self.__dict__.keys():
            yield key

    def __getitem__(self, key: str) -> str:
        compat_name = self._get_compat_key_name(key)
        try:
            return getattr(self, compat_name)
        except AttributeError as exc:
            raise KeyError() from exc

    @classmethod
    def from_dict(
            cls, values: dict[str, str]) -> 'PygeoapiMetadataContactConfiguration':
        return cls(
            name=values['name'],
            position=values['position'],
            address=values.get('address', ''),
            city=values.get('city', ''),
            state_or_province=values.get('stateorprovince', ''),
            postal_code=values.get('postalcode', ''),
            country=values.get('country', ''),
            phone=values.get('phone', ''),
            fax=values.get('fax', ''),
            email=values['email'],
            url=values.get('url', ''),
            hours_of_service=values.get('hours', ''),
            instructions=values.get('instructions', ''),
            role=values['role'],
        )

    @classmethod
    def _get_compat_key_name(cls, key: str) -> str:
        return {
            'stateorprovince': 'state_or_province',
            'postalcode': 'postal_code',
            'hours': 'hours_of_service',
        }.get(key, key)

    def get(self, key: str, default: Any = None) -> Any:
        compat_name = self._get_compat_key_name(key)
        try:
            return self.__getitem__(compat_name)
        except KeyError:
            return default


@dataclasses.dataclass
class PygeoapiMetadataConfiguration:
    """Implements the `MetadataConfiguration` protocol"""
    identification: PygeoapiMetadataIdentificationConfiguration
    license: PygeoapiMetadataLicenseConfiguration
    provider: PygeoapiMetadataProviderConfiguration
    contact: PygeoapiMetadataContactConfiguration

    def __iter__(self) -> Iterator[str]:
        for key in self.__dict__.keys():
            yield key

    def __getitem__(self, key: str) -> (
            PygeoapiMetadataIdentificationConfiguration |
            PygeoapiMetadataLicenseConfiguration |
            PygeoapiMetadataProviderConfiguration
    ):
        try:
            return getattr(self, key)
        except AttributeError as exc:
            raise KeyError() from exc

    @classmethod
    def from_dict(
            cls,
            values: dict[
                str,
                str | list[str] | dict[str, str]
            ]
    ) -> 'PygeoapiMetadataConfiguration':
        return cls(
            identification=PygeoapiMetadataIdentificationConfiguration.from_dict(
                values['identification']),
            license=PygeoapiMetadataLicenseConfiguration.from_dict(
                values['license']),
            provider=PygeoapiMetadataProviderConfiguration.from_dict(
                values['provider']),
            contact=PygeoapiMetadataContactConfiguration.from_dict(
                values['contact']),
        )

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


@dataclasses.dataclass
class PygeoapiLoggingConfiguration:
    level: str

    def __iter__(self) -> Iterator[str]:
        for key in self.__dict__.keys():
            yield key

    def __getitem__(self, key: str) -> str:
        try:
            return getattr(self, key)
        except AttributeError as exc:
            raise KeyError() from exc

    @classmethod
    def from_dict(cls, values: dict[str, str]) -> 'PygeoapiLoggingConfiguration':
        return cls(
            level=values.get('level', 'warning').upper(),
        )

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


@dataclasses.dataclass
class PygeoapiServerBindConfiguration:
    host: str
    port: int

    def __iter__(self) -> Iterator[str]:
        for key in self.__dict__.keys():
            yield key

    def __getitem__(self, key: str) -> str | int:
        try:
            return getattr(self, key)
        except AttributeError as exc:
            raise KeyError() from exc

    @classmethod
    def from_dict(
            cls, values: dict[str, str | int]) -> 'PygeoapiServerBindConfiguration':
        return cls(
            host=values['host'],
            port=int(values['port']),
        )

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


@dataclasses.dataclass
class PygeoapiProcessManagerConfiguration:
    name: str
    connection: str | None = None
    output_dir: str | None = None
    processes: dict[str, dict[str, Any]] = dataclasses.field(default_factory=dict)

    def __iter__(self) -> Iterator[str]:
        for key in self.__dict__.keys():
            yield key

    def __getitem__(self, key: str) -> str | None:
        try:
            return getattr(self, key)
        except AttributeError as exc:
            raise KeyError() from exc

    def __setitem__(
            self,
            key: Literal['processes'],
            value: dict[str, dict[str, Any]]
    ) -> None:
        """Assign a configuration value using a dict-like interface.

        Compatibility note: This method exists in order to allow the
        `pygeoapi.process.manager.get_manager()` function to mutate the
        process manager configuration, specifically to allow it to provide
        process definitions to it. This pattern is used to overcome the fact
        that the process manager initialization needs access to configured
        process definitions but these are specified in the 'resources' key of
        the config.
        """
        if key == 'processes':
            self.processes = value.copy()
        else:
            raise RuntimeError(
                'Modification of configuration via __setitem__ is not allowed')

    @classmethod
    def from_dict(
            cls, values: dict[str, str]) -> 'PygeoapiProcessManagerConfiguration':
        return cls(
            name=values['name'],
            connection=values.get('connection'),
            output_dir=values.get('output_dir'),
        )

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


@dataclasses.dataclass
class PygeoapiMapConfiguration:
    url: str
    attribution: str

    def __iter__(self) -> Iterator[str]:
        for key in self.__dict__.keys():
            yield key

    def __getitem__(self, key: str) -> str:
        try:
            return getattr(self, key)
        except AttributeError as exc:
            raise KeyError() from exc

    @classmethod
    def from_dict(
            cls, values: dict[str, str]) -> 'PygeoapiMapConfiguration':
        return cls(
            url=values['url'],
            attribution=values['attribution'],
        )

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


@dataclasses.dataclass
class PygeoapiServerConfiguration:
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
    map: PygeoapiMapConfiguration
    process_manager: PygeoapiProcessManagerConfiguration | None
    ogc_schemas_location: str | None

    def __iter__(self) -> Iterator[str]:
        for key in self.__dict__.keys():
            yield key

    def __getitem__(self, key: str) -> (
            bool | int | str |
            dict[str, str] | list[str],
            None |
            PygeoapiProcessManagerConfiguration |
            PygeoapiServerBindConfiguration,
    ):
        if key == 'templates':
            return {
                'path': self.templates_path,
                'static': self.static_path,
            }
        else:
            compat_name = self._get_compat_key_name(key)
            try:
                return getattr(self, compat_name)
            except AttributeError as exc:
                raise KeyError() from exc

    def __contains__(self, item: str) -> bool:
        """Check whether `item` is a property.

        Compatibility note: This method exists in order to overcome pygeoapi's
        `pygeoapi.api.API` class wanting to rewrite the config if it does not
        find a 'templates' key in there.
        """
        if item == "templates":
            return True
        else:
            compat_name = self._get_compat_key_name(item)
            return compat_name in self.__dict__.keys()

    @classmethod
    def _get_compat_key_name(cls, key: str) -> str:
        return {
            'admin': 'enable_admin',
            'cors': 'enable_cors',
            'gzip': 'gzip_responses',
            'manager': 'process_manager',
            'pretty_print': 'pretty_print_responses',
            'url': 'public_url',
        }.get(key, key)

    @classmethod
    def from_dict(
            cls,
            values: dict[
                str,
                bool | str | int | dict[str, str] | list[str]
            ]
    ) -> 'PygeoapiServerConfiguration':
        default_templates_path = Path(__file__).parent / 'templates'
        default_static_path = Path(__file__).parent / 'static'
        process_manager_conf = PygeoapiProcessManagerConfiguration(
            name='Dummy')
        if (raw_process_manager_conf := values.get('manager')) is not None:
            process_manager_conf = PygeoapiProcessManagerConfiguration.from_dict(
                raw_process_manager_conf)
        return cls(
            enable_admin=values['admin'],
            bind=PygeoapiServerBindConfiguration.from_dict(values['bind']),
            public_url=values['url'],
            mimetype=values.get('mimetype', 'application/json; charset=UTF-8'),
            encoding=values.get('encoding', 'utf-8'),
            gzip_responses=values.get('gzip', False),
            languages=values.get(
                'languages', ['en']
            ),
            enable_cors=values.get('cors', False),
            pretty_print_responses=values.get('pretty_print', False),
            limit=values.get('limit', 10),
            templates_path=values.get(
                'templates', {}).get('path', default_templates_path),
            static_path=values.get(
                'templates', {}).get('static', default_static_path),
            map=PygeoapiMapConfiguration.from_dict(values['map']),
            process_manager=process_manager_conf,
            ogc_schemas_location=values.get('ogc_schemas_location'),
        )

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


@dataclasses.dataclass
class PygeoapiConfiguration:
    """Default implementation of ConfigurationManager."""

    metadata: PygeoapiMetadataConfiguration
    logging: PygeoapiLoggingConfiguration
    server: PygeoapiServerConfiguration
    resources: dict[str, Any]

    def __iter__(self) -> Iterator[str]:
        for key in self.__dict__.keys():
            yield key

    def __getitem__(self, key: str) -> (
            PygeoapiMetadataConfiguration | PygeoapiLoggingConfiguration |
            PygeoapiServerConfiguration | dict[str, Any]
    ):
        try:
            return getattr(self, key)
        except AttributeError as exc:
            raise KeyError() from exc

    @classmethod
    def from_configuration_file(cls, configuration_file_path: str):
        if (conf_path := Path(configuration_file_path)).exists():
            with conf_path.open('r', encoding='utf-8') as fh:
                raw_conf = yaml_load(fh)
            return cls(
                metadata=PygeoapiMetadataConfiguration.from_dict(raw_conf['metadata']),
                logging=PygeoapiLoggingConfiguration.from_dict(raw_conf['logging']),
                server=PygeoapiServerConfiguration.from_dict(raw_conf['server']),
                resources=dict(raw_conf['resources']),
            )
        else:
            raise RuntimeError(f'Configuration file {configuration_file_path} does not exist')

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def as_dict(self) -> dict[str, dict[str, Any]]:
        return dataclasses.asdict(self)


def _parse_multilingual_string(
        value: str | dict[str, str],
        default_language_code: str = 'en'
) -> dict[str, str]:
    if isinstance(value, str):
        return {default_language_code: value}
    else:
        return value.copy()
