from djmodels.apps import AppConfig
from djmodels.utils.translation import gettext_lazy as _


class SyndicationConfig(AppConfig):
    name = 'djmodels.contrib.syndication'
    verbose_name = _("Syndication")
