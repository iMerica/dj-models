from djmodels.contrib.gis.db.backends.base.features import BaseSpatialFeatures
from djmodels.db.backends.sqlite3.features import (
    DatabaseFeatures as SQLiteDatabaseFeatures,
)
from djmodels.utils.functional import cached_property


class DatabaseFeatures(BaseSpatialFeatures, SQLiteDatabaseFeatures):
    supports_3d_storage = True

    @cached_property
    def supports_area_geodetic(self):
        return bool(self.connection.ops.lwgeom_version())
