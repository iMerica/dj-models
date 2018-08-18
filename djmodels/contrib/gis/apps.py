from djmodels.apps import AppConfig
from djmodels.core import serializers
from djmodels.utils.translation import gettext_lazy as _


class GISConfig(AppConfig):
    name = 'djmodels.contrib.gis'
    verbose_name = _("GIS")

    def ready(self):
        serializers.BUILTIN_SERIALIZERS.setdefault('geojson', 'djmodels.contrib.gis.serializers.geojson')
