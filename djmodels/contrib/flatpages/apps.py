from djmodels.apps import AppConfig
from djmodels.utils.translation import gettext_lazy as _


class FlatPagesConfig(AppConfig):
    name = 'djmodels.contrib.flatpages'
    verbose_name = _("Flat Pages")
