import unittest

from forms_tests.widget_tests.base import WidgetTest

from djmodels.db import connection
from djmodels.db.backends.signals import connection_created
from djmodels.test import TestCase, modify_settings


@unittest.skipUnless(connection.vendor == 'postgresql', "PostgreSQL specific tests")
class PostgreSQLTestCase(TestCase):
    @classmethod
    def tearDownClass(cls):
        # No need to keep that signal overhead for non PostgreSQL-related tests.
        from djmodels.contrib.postgres.signals import register_type_handlers

        connection_created.disconnect(register_type_handlers)
        super().tearDownClass()


@unittest.skipUnless(connection.vendor == 'postgresql', "PostgreSQL specific tests")
# To locate the widget's template.
@modify_settings(INSTALLED_APPS={'append': 'djmodels.contrib.postgres'})
class PostgreSQLWidgetTestCase(WidgetTest, PostgreSQLTestCase):
    pass
