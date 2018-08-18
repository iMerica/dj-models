import logging

from djmodels.conf import settings
from djmodels.contrib.gis import gdal
from djmodels.contrib.gis.geometry import json_regex
from djmodels.contrib.gis.geos import GEOSException, GEOSGeometry
from djmodels.forms.widgets import Widget
from djmodels.utils import translation

logger = logging.getLogger('djmodels.contrib.gis')


class BaseGeometryWidget(Widget):
    """
    The base class for rich geometry widgets.
    Render a map using the WKT of the geometry.
    """
    geom_type = 'GEOMETRY'
    map_srid = 4326
    map_width = 600
    map_height = 400
    display_raw = False

    supports_3d = False
    template_name = ''  # set on subclasses

    def __init__(self, attrs=None):
        self.attrs = {}
        for key in ('geom_type', 'map_srid', 'map_width', 'map_height', 'display_raw'):
            self.attrs[key] = getattr(self, key)
        if attrs:
            self.attrs.update(attrs)

    def serialize(self, value):
        return value.wkt if value else ''

    def deserialize(self, value):
        try:
            return GEOSGeometry(value)
        except (GEOSException, ValueError, TypeError) as err:
            logger.error("Error creating geometry from value '%s' (%s)", value, err)
        return None

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        # If a string reaches here (via a validation error on another
        # field) then just reconstruct the Geometry.
        if value and isinstance(value, str):
            value = self.deserialize(value)

        if value:
            # Check that srid of value and map match
            if value.srid and value.srid != self.map_srid:
                try:
                    ogr = value.ogr
                    ogr.transform(self.map_srid)
                    value = ogr
                except gdal.GDALException as err:
                    logger.error(
                        "Error transforming geometry from srid '%s' to srid '%s' (%s)",
                        value.srid, self.map_srid, err
                    )

        context.update(self.build_attrs(self.attrs, {
            'name': name,
            'module': 'geodjango_%s' % name.replace('-', '_'),  # JS-safe
            'serialized': self.serialize(value),
            'geom_type': gdal.OGRGeomType(self.attrs['geom_type']),
            'STATIC_URL': settings.STATIC_URL,
            'LANGUAGE_BIDI': translation.get_language_bidi(),
            **(attrs or {}),
        }))
        return context


class OpenLayersWidget(BaseGeometryWidget):
    template_name = 'gis/openlayers.html'
    map_srid = 3857

    class Media:
        css = {
            'all': (
                'https://cdnjs.cloudflare.com/ajax/libs/ol3/4.6.5/ol.css',
                'gis/css/ol3.css',
            )
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/ol3/4.6.5/ol.js',
            'gis/js/OLMapWidget.js',
        )

    def serialize(self, value):
        return value.json if value else ''

    def deserialize(self, value):
        geom = super().deserialize(value)
        # GeoJSON assumes WGS84 (4326). Use the map's SRID instead.
        if geom and json_regex.match(value) and self.map_srid != 4326:
            geom.srid = self.map_srid
        return geom


class OSMWidget(OpenLayersWidget):
    """
    An OpenLayers/OpenStreetMap-based widget.
    """
    template_name = 'gis/openlayers-osm.html'
    default_lon = 5
    default_lat = 47
    default_zoom = 12

    def __init__(self, attrs=None):
        super().__init__()
        for key in ('default_lon', 'default_lat', 'default_zoom'):
            self.attrs[key] = getattr(self, key)
        if attrs:
            self.attrs.update(attrs)