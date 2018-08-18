from djmodels.apps import AppConfig
from djmodels.utils.translation import gettext_lazy as _


class HumanizeConfig(AppConfig):
    name = 'djmodels.contrib.humanize'
    verbose_name = _("Humanize")
