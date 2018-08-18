from djmodels.apps import AppConfig
from djmodels.db import connections
from djmodels.db.backends.signals import connection_created
from djmodels.db.models import CharField, TextField
from djmodels.utils.translation import gettext_lazy as _

from .lookups import SearchLookup, TrigramSimilar, Unaccent
from .signals import register_type_handlers


class PostgresConfig(AppConfig):
    name = 'djmodels.contrib.postgres'
    verbose_name = _('PostgreSQL extensions')

    def ready(self):
        # Connections may already exist before we are called.
        for conn in connections.all():
            if conn.vendor == 'postgresql':
                conn.introspection.data_types_reverse.update({
                    3802: 'djmodels.contrib.postgres.fields.JSONField',
                    3904: 'djmodels.contrib.postgres.fields.IntegerRangeField',
                    3906: 'djmodels.contrib.postgres.fields.FloatRangeField',
                    3910: 'djmodels.contrib.postgres.fields.DateTimeRangeField',
                    3912: 'djmodels.contrib.postgres.fields.DateRangeField',
                    3926: 'djmodels.contrib.postgres.fields.BigIntegerRangeField',
                })
                if conn.connection is not None:
                    register_type_handlers(conn)
        connection_created.connect(register_type_handlers)
        CharField.register_lookup(Unaccent)
        TextField.register_lookup(Unaccent)
        CharField.register_lookup(SearchLookup)
        TextField.register_lookup(SearchLookup)
        CharField.register_lookup(TrigramSimilar)
        TextField.register_lookup(TrigramSimilar)
