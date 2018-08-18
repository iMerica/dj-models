from djmodels.conf.urls import url
from djmodels.conf.urls.i18n import i18n_patterns
from djmodels.http import HttpResponse, StreamingHttpResponse
from djmodels.utils.translation import gettext_lazy as _

urlpatterns = i18n_patterns(
    url(r'^simple/$', lambda r: HttpResponse()),
    url(r'^streaming/$', lambda r: StreamingHttpResponse([_("Yes"), "/", _("No")])),
)
