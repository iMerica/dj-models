from djmodels.db import connection
from djmodels.test import SimpleTestCase

from .fields import CustomTypedField


class TestDbType(SimpleTestCase):

    def test_db_parameters_respects_db_type(self):
        f = CustomTypedField()
        self.assertEqual(f.db_parameters(connection)['type'], 'custom_field')
