from djmodels.conf.urls import include, url
from djmodels.conf.urls.i18n import i18n_patterns
from djmodels.utils.translation import gettext_lazy as _

urlpatterns = i18n_patterns(
    url(_(r'^account/'), include('i18n.patterns.urls.wrong_namespace', namespace='account')),
)
