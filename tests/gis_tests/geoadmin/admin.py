from djmodels.contrib.gis import admin


class UnmodifiableAdmin(admin.OSMGeoAdmin):
    modifiable = False
