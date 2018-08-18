"""
 This module contains useful utilities for GeoDjango.
"""
from djmodels.contrib.gis.utils.ogrinfo import ogrinfo  # NOQA
from djmodels.contrib.gis.utils.ogrinspect import mapping, ogrinspect  # NOQA
from djmodels.contrib.gis.utils.srs import add_srs_entry  # NOQA
from djmodels.core.exceptions import ImproperlyConfigured

try:
    # LayerMapping requires DJANGO_SETTINGS_MODULE to be set,
    # and ImproperlyConfigured is raised if that's not the case.
    from djmodels.contrib.gis.utils.layermapping import LayerMapping, LayerMapError  # NOQA
except ImproperlyConfigured:
    pass
