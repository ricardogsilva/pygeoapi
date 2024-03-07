# Install GDAL and respective Python bindings
# This script is meant to be run by a user with administrative privileges
# on the system

apt update && \
apt install --yes software-properties-common && \
add-apt-repository --yes ppa:ubuntugis/ubuntugis-unstable && \
apt update && \
apt install --yes \
    libgdal-dev \
    gdal-bin && \
pip3 install --global-option=build_ext --global-option="-I/usr/include/gdal" GDAL==`gdal-config --version`
