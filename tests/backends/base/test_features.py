from djmodels.db import connection
from djmodels.test import TestCase


class TestDatabaseFeatures(TestCase):

    def test_nonexistent_feature(self):
        self.assertFalse(hasattr(connection.features, 'nonexistent'))
