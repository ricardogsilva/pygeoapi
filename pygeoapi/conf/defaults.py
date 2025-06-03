from pathlib import Path

DEFAULT_ENCODING = 'utf-8'
DEFAULT_SPATIAL_CRS = 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'
DEFAULT_MEDIA_TYPE = 'application/json; charset=UTF-8'
DEFAULT_TEMPLATES_PATH = Path(__file__).parents[1] / 'templates'
DEFAULT_STATIC_PATH = Path(__file__).parents[1] / 'static'
