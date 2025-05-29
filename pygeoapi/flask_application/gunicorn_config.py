"""gunicorn configuration file

You can launch your pygeoapi application via gunicorn like this:

```
export PYGEOAPI_CONFIG=example-config.yml
gunicorn -c python:pygeoapi.flask_application.gunicorn_config "pygeoapi.flask_application:get_app()"
```

Or, a more involved setup, with a custom log configuration and a different configuration
manager:

```
export PYGEOAPI_LOG_CONFIG=example-log-config.yml
export PYGEOAPI_CONFIG_INITIALIZER=pygeoapi.conf.shared.PygeoapiSharedConfiguration:from_env_variable
export PYGEOAPI_CONFIG=example-config.yml
gunicorn -c python:pygeoapi.flask_application.gunicorn_config "pygeoapi.flask_application:get_app()"
```

You may configure the following gunicorn parameters via environment variables:

- bind address: set the 'PYGEOAPI_BIND_ADDRESS' variable
- bind port: set the 'PYGEOAPI_BIND_PORT' variable
- number of worker processes: set the 'PYGEOAPI_NUM_WORKERS' variable

"""

import os
import logging.config
from pygeoapi.log import ENV_LOGGING_CONFIG

if ENV_LOGGING_CONFIG is not None:
    logging.config.dictConfig(ENV_LOGGING_CONFIG)

_DEFAULT_BIND_ADDRESS = 'localhost'
_DEFAULT_BIND_PORT = 5000

bind=(
    f'{os.getenv("PYGEOAPI_BIND_ADDRESS", _DEFAULT_BIND_ADDRESS)}:'
    f'{os.getenv("PYGEOAPI_BIND_PORT", _DEFAULT_BIND_PORT)}'
)
workers = os.getenv('PYGEOAPI_NUM_WORKERS', 4)
accesslog = '-'
loglevel = 'debug'