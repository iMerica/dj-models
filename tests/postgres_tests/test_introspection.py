from io import StringIO

from djmodels.core.management import call_command
from djmodels.test.utils import modify_settings

from . import PostgreSQLTestCase


@modify_settings(INSTALLED_APPS={'append': 'djmodels.contrib.postgres'})
class InspectDBTests(PostgreSQLTestCase):
    def assertFieldsInModel(self, model, field_outputs):
        out = StringIO()
        call_command(
            'inspectdb',
            table_name_filter=lambda tn: tn.startswith(model),
            stdout=out,
        )
        output = out.getvalue()
        for field_output in field_outputs:
            self.assertIn(field_output, output)

    def test_json_field(self):
        self.assertFieldsInModel(
            'postgres_tests_jsonmodel',
            ['field = djmodels.contrib.postgres.fields.JSONField(blank=True, null=True)'],
        )

    def test_range_fields(self):
        self.assertFieldsInModel(
            'postgres_tests_rangesmodel',
            [
                'ints = djmodels.contrib.postgres.fields.IntegerRangeField(blank=True, null=True)',
                'bigints = djmodels.contrib.postgres.fields.BigIntegerRangeField(blank=True, null=True)',
                'floats = djmodels.contrib.postgres.fields.FloatRangeField(blank=True, null=True)',
                'timestamps = djmodels.contrib.postgres.fields.DateTimeRangeField(blank=True, null=True)',
                'dates = djmodels.contrib.postgres.fields.DateRangeField(blank=True, null=True)',
            ],
        )
