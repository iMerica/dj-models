import warnings

from djmodels.utils.deprecation import RemovedInDjango30Warning

warnings.warn(
    "The djmodels.db.backends.postgresql_psycopg2 module is deprecated in "
    "favor of djmodels.db.backends.postgresql.",
    RemovedInDjango30Warning, stacklevel=2
)
