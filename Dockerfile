# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#          Just van den Broecke <justb4@gmail.com>
#          Francesco Bartoli <xbartolone@gmail.com>
#          Ricardo Garcia Silva <ricardo.garcia.silva@gmail.com>
#
# Copyright (c) 2020 Tom Kralidis
# Copyright (c) 2019 Just van den Broecke
# Copyright (c) 2020 Francesco Bartoli
# Copyright (c) 2020 Ricardo Garcia Silva
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

FROM osgeo/gdal:ubuntu-small-3.1.3

LABEL maintainer="Just van den Broecke <justb4@gmail.com>"

# Docker file for full geoapi server with libs/packages for all providers.
# Server runs with gunicorn. You can override ENV settings.
# Defaults:
# SCRIPT_NAME=/
# CONTAINER_NAME=pygeoapi
# CONTAINER_HOST=0.0.0.0
# CONTAINER_PORT=80
# WSGI_WORKERS=4
# WSGI_WORKER_TIMEOUT=6000
# WSGI_WORKER_CLASS=gevent

# Calls entrypoint.sh to run. Inspect it for options.
# Contains some test data. Also allows you to verify by running all unit tests.
# Simply run: docker run -it geopython/pygeoapi test
# Override the default config file /pygeoapi/local.config.yml
# via Docker Volume mapping or within a docker-compose.yml file. See example at
# https://github.com/geopython/demo.pygeoapi.io/tree/master/services/pygeoapi

# ARGS
ARG TIMEZONE="Europe/London"
ARG LOCALE="en_US.UTF-8"
ARG ADD_DEB_PACKAGES=""
ARG ADD_PIP_PACKAGES=""

# ENV settings
ENV TZ=${TIMEZONE} \
	DEBIAN_FRONTEND="noninteractive" \
	PIP_PACKAGES="gunicorn==20.0.4 gevent==1.5a4 wheel==0.33.4 ${ADD_PIP_PACKAGES}"

RUN \
	# Install dependencies
	apt-get update \
	&& apt-get install --yes \
	  locales \
	  python3-venv \
	  tzdata \
	  unzip \
	  ${ADD_DEB_PACKAGES} \
	# Timezone
	&& cp /usr/share/zoneinfo/${TZ} /etc/localtime\
	&& dpkg-reconfigure tzdata \
	# Locale
	&& sed -i -e "s/# ${LOCALE} UTF-8/${LOCALE} UTF-8/" /etc/locale.gen \
	&& dpkg-reconfigure --frontend=noninteractive locales \
	&& update-locale LANG=${LOCALE} \
	&& echo "For ${TZ} date=$(date)" && echo "Locale=$(locale)" \
	# download get-poetry script
    && curl \
      --silent \
      --show-error \
      --location https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py > /opt/get-poetry.py \
	# Cleanup TODO: remove unused Locales and TZs
	&& apt autoremove --yes  \
	&& rm -rf /var/lib/apt/lists/*

RUN adduser --gecos "" --disabled-password geopython

USER geopython

WORKDIR /home/geopython

COPY --chown=geopython:geopython docker/default.config.yml local.config.yml
COPY --chown=geopython:geopython docker/entrypoint.sh entrypoint.sh


# install poetry and create a virtualenv with site-packages for it
RUN python3 /opt/get-poetry.py --yes --version=1.1.0 \
	&& python3 -m venv --system-site-packages /home/geopython/venv

ENV PATH="$PATH:/home/geopython/.poetry/bin"

RUN mkdir schemas.opengis.net \
	&& curl -O http://schemas.opengis.net/SCHEMAS_OPENGIS_NET.zip \
	&& unzip ./SCHEMAS_OPENGIS_NET.zip "ogcapi/*" -d schemas.opengis.net

COPY --chown=geopython:geopython pyproject.toml poetry.lock pygeoapi/

WORKDIR /home/geopython/pygeoapi

SHELL ["/bin/bash", "-c", "source /home/geopython/venv/bin/activate"]

RUN \
    poetry install --no-root \
    && poetry run pip install ${PIP_PACKAGES}

COPY --chown=geopython:geopython . .

RUN \
    source /home/geopython/venv/bin/python \
    && poetry install

WORKDIR /home/geopython

ENTRYPOINT ["./entrypoint.sh"]
