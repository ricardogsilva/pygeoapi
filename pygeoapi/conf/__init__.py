from pygeoapi.conf.protocols import (
    ConfigurationManager,
    ConfigurationInitializer,
)

from pygeoapi.conf.readonly import PygeoapiConfiguration
from pygeoapi.util import import_object


def initialize_configuration(
        config_initializer_name: str | None = None
) -> ConfigurationManager:
    if config_initializer_name is None:
        initializer = PygeoapiConfiguration.from_env_variable
    else:
        initializer = import_object(config_initializer_name)
    initializer: ConfigurationInitializer
    return initializer()
