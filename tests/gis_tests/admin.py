try:
    from djmodels.contrib.gis import admin
except ImportError:
    from djmodels.contrib import admin

    admin.OSMGeoAdmin = admin.ModelAdmin
