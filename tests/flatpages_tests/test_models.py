from djmodels.contrib.flatpages.models import FlatPage
from djmodels.test import SimpleTestCase
from djmodels.test.utils import override_script_prefix


class FlatpageModelTests(SimpleTestCase):

    def setUp(self):
        self.page = FlatPage(title='Café!', url='/café/')

    def test_get_absolute_url_urlencodes(self):
        self.assertEqual(self.page.get_absolute_url(), '/caf%C3%A9/')

    @override_script_prefix('/prefix/')
    def test_get_absolute_url_honors_script_prefix(self):
        self.assertEqual(self.page.get_absolute_url(), '/prefix/caf%C3%A9/')

    def test_str(self):
        self.assertEqual(str(self.page), '/café/ -- Café!')
