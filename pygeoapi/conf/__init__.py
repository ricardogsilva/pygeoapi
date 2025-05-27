"""pygeoapi configuration management utilities."""

import dataclasses
import os
from functools import partial
from pathlib import Path
from typing import (
    Any,
    Iterator,
    Literal,
    Sequence,
    Union,
)

from pygeoapi.util import yaml_load
from pygeoapi.conf.protocols import (
    InternationalizationArray,
    InternationalizationString, CollectionResourceConfiguration,
)

_default_crs = 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'
_default_crs_list = partial(list, [_default_crs])


@dataclasses.dataclass
class PygeoapiLinkConfiguration:
    type: str
    rel: str
    href: str
    title: str | None = None
    hreflang: str | None = None
    length: str | None = None

    @classmethod
    def from_dict(
            cls,
            values: dict[str, str | None]
    ) -> 'PygeoapiLinkConfiguration':
        return cls(**{k: v for k, v in values.items() if v is not None})


class DictLikeRead:

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

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


@dataclasses.dataclass
class PygeoapiMetadataIdentificationConfiguration(DictLikeRead):
    """Implements the `MetadataIdentificationConfiguration` protocol"""
    title: dict[str, str]
    description: dict[str, str]
    keywords: dict[str, list[str]]
    keywords_type: str
    terms_of_service: str
    url: str

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


@dataclasses.dataclass
class PygeoapiMetadataLicenseConfiguration(DictLikeRead):
    name: str
    url: str

    @classmethod
    def from_dict(
            cls, values: dict[str, str]) -> 'PygeoapiMetadataLicenseConfiguration':
        return cls(
            name=values['name'],
            url=values.get('url'),
        )


@dataclasses.dataclass
class PygeoapiMetadataProviderConfiguration(DictLikeRead):
    name: str
    url: str

    @classmethod
    def from_dict(
            cls, values: dict[str, str]) -> 'PygeoapiMetadataProviderConfiguration':
        return cls(
            name=values['name'],
            url=values.get('url'),
        )


@dataclasses.dataclass
class PygeoapiMetadataContactConfiguration(DictLikeRead):
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
class PygeoapiMetadataConfiguration(DictLikeRead):
    """Implements the `MetadataConfiguration` protocol"""
    identification: PygeoapiMetadataIdentificationConfiguration
    license: PygeoapiMetadataLicenseConfiguration
    provider: PygeoapiMetadataProviderConfiguration
    contact: PygeoapiMetadataContactConfiguration

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


@dataclasses.dataclass
class PygeoapiProcessManagerConfiguration(DictLikeRead):
    name: str
    connection: str | None = None
    output_dir: str | None = None
    processes: dict[str, dict[str, Any]] = dataclasses.field(default_factory=dict)

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


@dataclasses.dataclass
class PygeoapiMapConfiguration(DictLikeRead):
    url: str
    attribution: str

    @classmethod
    def from_dict(
            cls, values: dict[str, str]) -> 'PygeoapiMapConfiguration':
        return cls(
            url=values['url'],
            attribution=values['attribution'],
        )


@dataclasses.dataclass
class PygeoapiServerConfiguration(DictLikeRead):
    enable_admin: bool
    public_url: str
    mimetype: str
    encoding: str
    languages: list[str]
    pretty_print_responses: bool
    limit: int
    templates_path: str
    static_path: str
    map: PygeoapiMapConfiguration
    process_manager: PygeoapiProcessManagerConfiguration | None
    ogc_schemas_location: str | None

    def __getitem__(self, key: str) -> (
            bool | int | str |
            dict[str, str] | list[str],
            None |
            PygeoapiProcessManagerConfiguration
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
            public_url=values['url'],
            mimetype=values.get('mimetype', 'application/json; charset=UTF-8'),
            encoding=values.get('encoding', 'utf-8'),
            languages=values.get(
                'languages', ['en']
            ),
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


@dataclasses.dataclass
class PygeoapiCollectionResourceSpatialExtentConfiguration(DictLikeRead):
    bbox: tuple[float, float, float, float] | tuple[float, float, float, float, float, float]
    crs: str = 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'

    @classmethod
    def from_dict(
            cls,
            values: dict[
                str,
                str |
                tuple[float, float, float, float] |
                tuple[float, float, float, float, float, float]
            ]
    ) -> 'PygeoapiCollectionResourceSpatialExtentConfiguration':
        return cls(**{k: v for k, v in values.items() if v is not None})


@dataclasses.dataclass
class PygeoapiCollectionResourceTemporalExtentConfiguration(DictLikeRead):
    begin: str | None = None
    end: str | None = None
    trs: str = 'http://www.opengis.net/def/uom/ISO-8601/0/Gregorian'

    @classmethod
    def from_dict(
            cls,
            values: dict[str, str | None]
    ) -> 'PygeoapiCollectionResourceTemporalExtentConfiguration':
        return cls(**{k: v for k, v in values.items() if v is not None})


@dataclasses.dataclass
class PygeoapiCollectionResourceExtentsConfiguration(DictLikeRead):
    spatial: PygeoapiCollectionResourceSpatialExtentConfiguration
    temporal: PygeoapiCollectionResourceTemporalExtentConfiguration | None = None

    @classmethod
    def from_dict(
            cls,
            values: dict[str, dict[str, str | list[float]]]
    ) -> 'PygeoapiCollectionResourceExtentsConfiguration':
        return cls(
            spatial=PygeoapiCollectionResourceSpatialExtentConfiguration.from_dict(
                values['spatial']),
            temporal=(
                PygeoapiCollectionResourceTemporalExtentConfiguration.from_dict(
                    raw_temporal_conf
                ) if (raw_temporal_conf := values.get('temporal')) is not None
                else None
            ),
        )


@dataclasses.dataclass
class PygeoapiCollectionProviderGeometryConfiguration(DictLikeRead):
    x_field: str
    y_field: str

    @classmethod
    def from_dict(
            cls,
            values: dict[str, str]
    ) -> 'PygeoapiCollectionProviderGeometryConfiguration':
        return cls(
            x_field=values['x_field'],
            y_field=values['y_field'],
        )


@dataclasses.dataclass
class PygeoapiCollectionProviderMediaTypeConfiguration(DictLikeRead):
    name: str
    media_type: str

    @classmethod
    def _get_compat_key_name(cls, key: str) -> str:
        return {
            'mimetype': 'media_type',
        }.get(key, key)

    @classmethod
    def from_dict(
            cls,
            values: dict[str, str]
    ) -> 'PygeoapiCollectionProviderMediaTypeConfiguration':
        return cls(
            name=values['name'],
            media_type=values['mimetype'],
        )

    def __getitem__(self, key: str) -> str:
        compat_name = self._get_compat_key_name(key)
        try:
            return getattr(self, compat_name)
        except AttributeError as exc:
            raise KeyError() from exc


@dataclasses.dataclass
class PygeoapiCollectionProviderConfiguration(DictLikeRead):
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
    is_default: bool = False
    is_editable: bool = False
    table: str | None = None
    id_field: str | None = None
    geometry: PygeoapiCollectionProviderGeometryConfiguration | None = None
    time_field: str | None = None
    title_field: str | None = None
    default_format: PygeoapiCollectionProviderMediaTypeConfiguration | None = None
    options: dict[str, Any] | None = None
    public_properties: list[str] | None = None
    supported_crs: list[str] = dataclasses.field(default_factory=_default_crs_list)
    storage_crs: str = _default_crs
    storage_crs_coordinate_epoch: str | None = None

    @classmethod
    def _get_compat_key_name(cls, key: str) -> str:
        return {
            'default': 'is_default',
            'editable': 'is_editable',
            'format': 'default_format',
            'properties': 'public_properties',
            'crs': 'supported_crs',
        }.get(key, key)

    @classmethod
    def from_dict(
            cls,
            values: dict[
                str,
                str | bool | dict[str, Any]
            ]
    ) -> 'PygeoapiCollectionProviderConfiguration':
        return cls(
            type=values['type'],
            name=values['name'],
            data=(
                dict(raw_data)
                if isinstance(raw_data := values['data'], dict) else raw_data
            ),
            is_default=values.get('default', False),
            is_editable=values.get('editable', False),
            table=values.get('table', None),
            id_field=values.get('id_field', None),
            geometry=(
                PygeoapiCollectionProviderGeometryConfiguration.from_dict(
                    raw_geom
                ) if (raw_geom := values.get('geometry')) is not None
                else None
            ),
            time_field=values.get('time_field', None),
            title_field=values.get('title_field', None),
            default_format=(
                PygeoapiCollectionProviderMediaTypeConfiguration.from_dict(
                    raw_default_format
                ) if (raw_default_format := values.get('format')) is not None
                else None
            ),
            options=(
                dict(raw_options)
                if isinstance(raw_options := values.get('options'), dict)
                else None
            ),
            public_properties=(
                raw_properties[:]
                if (raw_properties := values.get('properties')) is not None
                else None
            ),
            supported_crs=(
                raw_crs[:]
                if (raw_crs := values.get('crs')) is not None
                else _default_crs_list()
            ),
            storage_crs=values.get('storage_crs', _default_crs),
            storage_crs_coordinate_epoch=values.get('storage_crs_coordinate_epoch'),
        )

    def __getitem__(self, key: str) -> str:
        compat_name = self._get_compat_key_name(key)
        try:
            return getattr(self, compat_name)
        except AttributeError as exc:
            raise KeyError() from exc


@dataclasses.dataclass
class PygeoapiLimitsConfiguration(DictLikeRead):
    max_items: int = 10
    default_items: int = 10
    max_distance_x: float | None = None
    max_distance_y: float | None = None
    max_distance_units: str | None = None
    on_exceed: Literal['error', 'throttle'] = 'throttle'

    @classmethod
    def from_dict(
            cls,
            values: dict[str, int | float | str | None]
    ) -> 'PygeoapiLimitsConfiguration':
        return cls(**{k: v for k, v in values.items() if v is not None})


@dataclasses.dataclass
class PygeoapiCollectionResourceConfiguration(DictLikeRead):
    identifier: str
    type: Literal[
        'collection',
        'stac-collection',
    ]
    title: InternationalizationString
    description: InternationalizationString
    keywords: InternationalizationArray
    extents: PygeoapiCollectionResourceExtentsConfiguration
    providers: list[PygeoapiCollectionProviderConfiguration]
    visibility: Literal['default', 'hidden'] = 'default'
    linked_data: dict[str, str | dict] | None = None
    links: list[PygeoapiLinkConfiguration] | None = None
    limits: PygeoapiLimitsConfiguration | None = None

    @classmethod
    def from_dict(
            cls,
            identifier: str,
            values: dict[str, str | dict[str, Any] | None]
    ) -> 'PygeoapiCollectionResourceConfiguration':
        if isinstance(raw_keywords := values['keywords'], dict):
            parsed_keywords = {
                lang_code: items[:]
                for lang_code, items in raw_keywords.items()
            }
        else:
            parsed_keywords = raw_keywords[:]

        return cls(
            identifier=identifier,
            type=values['type'],
            title=(
                dict(raw_title)
                if isinstance(raw_title := values['title'], dict)
                else raw_title
            ),
            description=(
                dict(raw_description)
                if isinstance(raw_description := values['description'], dict)
                else raw_description
            ),
            keywords=parsed_keywords,
            extents=PygeoapiCollectionResourceExtentsConfiguration.from_dict(
                values['extents']),
            providers=[
                PygeoapiCollectionProviderConfiguration.from_dict(raw_provider_conf)
                for raw_provider_conf in values['providers']
            ],
            visibility=values.get('visibility', 'default'),
            linked_data=(
                dict(raw_linked_data)
                if (raw_linked_data := values.get('linked_data')) is not None
                else None
            ),
            links=(
                [
                    PygeoapiLinkConfiguration.from_dict(raw_link)
                    for raw_link in raw_links
                ] if (raw_links := values.get('links')) is not None
                else None
            ),
            limits=(
                PygeoapiLimitsConfiguration.from_dict(raw_limits)
                if (raw_limits := values.get('limits')) is not None
                else None
            ),
        )


@dataclasses.dataclass
class PygeoapiProcessorConfiguration(DictLikeRead):
    name: str

    @classmethod
    def from_dict(cls, values: dict[str, str]) -> 'PygeoapiProcessorConfiguration':
        return cls(name=values['name'])


@dataclasses.dataclass
class PygeoapiProcessResourceConfiguration(DictLikeRead):
    identifier: str
    type: Literal['process']
    processor: PygeoapiProcessorConfiguration

    @classmethod
    def from_dict(
            cls, identifier: str, values: dict[str, str | dict[str, str]]
    ) -> 'PygeoapiProcessResourceConfiguration':
        return cls(
            identifier=identifier,
            type=values['type'],
            processor=PygeoapiProcessorConfiguration.from_dict(values['processor'])
        )


class PygeoapiResourcesConfiguration(DictLikeRead):
    _resources: dict

    def __init__(
            self,
            resources: Sequence[
                Union[
                    PygeoapiCollectionResourceConfiguration,
                    PygeoapiProcessResourceConfiguration
                ]
            ]
    ) -> None:
        self._resources = {
            resource.identifier: resource for resource in resources
        }

    def __iter__(self) -> Iterator[str]:
        for key in self._resources.keys():
            yield key

    def __getitem__(
            self,
            key: str
    ) -> Union[PygeoapiCollectionResourceConfiguration, PygeoapiProcessorConfiguration]:
        return self._resources[key]

    def get(self, resource_identifier: str, default: Any = None) -> Any:
        try:
            return self.__getitem__(resource_identifier)
        except KeyError:
            return default


# class PygeoapiResourceManager:
#     _resources: dict
#
#     def __init__(
#             self,
#             resources: Sequence[
#                 Union[
#                     PygeoapiCollectionResourceConfiguration,
#                     PygeoapiProcessResourceConfiguration
#                 ]
#             ]
#     ) -> None:
#         self._resources = {
#             resource.identifier: resource for resource in resources
#         }
#
#     def __iter__(self) -> Iterator[str]:
#         for key in self._resources.keys():
#             yield key
#
#     def __getitem__(
#             self,
#             key: str
#     ) -> Union[PygeoapiCollectionResourceConfiguration, PygeoapiProcessorConfiguration]:
#         return self._resources[key]
#
#     def get(self, resource_identifier: str, default: Any = None) -> Any:
#         try:
#             return self.__getitem__(resource_identifier)
#         except KeyError:
#             return default
#
#     def get_resource(self, resource_identifier: str) -> Union[
#             PygeoapiCollectionResourceConfiguration,
#             PygeoapiProcessResourceConfiguration
#     ]:
#         return self._resources[resource_identifier]
#
#     def list_resources(self, limit: int | None = None, offset: int = 0) -> list[
#         PygeoapiCollectionResourceConfiguration |
#         PygeoapiProcessResourceConfiguration
#     ]:
#         list_range = slice(
#             offset,
#             (offset + limit) if limit is not None else -1,
#         )
#         return list(self._resources.values())[list_range]
#
#     def create_resource(
#             self,
#             resource: Union[
#                 PygeoapiCollectionResourceConfiguration,
#                 PygeoapiProcessResourceConfiguration
#             ]
#     ) -> Union[
#         PygeoapiCollectionResourceConfiguration,
#         PygeoapiProcessResourceConfiguration
#     ]:
#         if resource.identifier in self._resources:
#             raise RuntimeError(
#                 f'Resource identified by {resource.identifier} already exists')
#         else:
#             self._resources[resource.identifier] = resource
#         return resource
#
#     def update_resource(
#             self,
#             resource: Union[
#                 PygeoapiCollectionResourceConfiguration,
#                 PygeoapiProcessResourceConfiguration
#             ]
#     ) -> Union[
#         PygeoapiCollectionResourceConfiguration,
#         PygeoapiProcessResourceConfiguration
#     ]:
#         if resource.identifier not in self._resources:
#             raise RuntimeError('Cannot update a resource that does not exist')
#         else:
#             self._resources[resource.identifier] = resource
#         return resource
#
#     def delete_resource(self, resource_identifier: str) -> bool:
#         try:
#             self._resources.pop(resource_identifier)
#             return True
#         except KeyError:
#             raise RuntimeError(
#                 f'Resource identified by {resource_identifier} does not exist')


@dataclasses.dataclass
class PygeoapiConfiguration(DictLikeRead):
    """Default implementation of ConfigurationManager."""

    metadata: PygeoapiMetadataConfiguration
    server: PygeoapiServerConfiguration
    resources: PygeoapiResourcesConfiguration
    # resources: dict[
    #     str,
    #     CollectionResourceConfiguration | ProcessResourceConfiguration
    # ]

    @classmethod
    def from_configuration_file(
            cls, configuration_file_path: str
    ) -> 'PygeoapiConfiguration':
        if (conf_path := Path(configuration_file_path)).exists():
            with conf_path.open('r', encoding='utf-8') as fh:
                raw_conf = yaml_load(fh)
            parsed_resources = []
            for resource_id, resource_conf in raw_conf.get('resources', {}).items():
                match resource_conf.get('type'):
                    case 'collection' | 'stac-collection':
                        parsed_resources.append(
                            PygeoapiCollectionResourceConfiguration.from_dict(
                                resource_id, resource_conf)
                        )
                    case 'process':
                        parsed_resources.append(
                            PygeoapiProcessResourceConfiguration.from_dict(
                                resource_id, resource_conf)
                        )
                    case _:
                        raise RuntimeError(f'Unrecognized resource type: {_}')
            return cls(
                metadata=PygeoapiMetadataConfiguration.from_dict(raw_conf['metadata']),
                server=PygeoapiServerConfiguration.from_dict(raw_conf['server']),
                resources=PygeoapiResourcesConfiguration(parsed_resources)
                # resources={
                #     resource.identifier: resource for resource in parsed_resources},
            )
        else:
            raise RuntimeError(f'Configuration file {configuration_file_path} does not exist')

    @classmethod
    def from_env_variable(cls) -> 'PygeoapiConfiguration':
        if (config_path := os.getenv('PYGEOAPI_CONFIG')) is not None:
            return cls.from_configuration_file(config_path)
        else:
            raise RuntimeError('PYGEOAPI_CONFIG environment variable not set')

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
