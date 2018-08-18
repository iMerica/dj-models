from djmodels.conf.urls import url
from djmodels.conf.urls.i18n import i18n_patterns
from djmodels.http import HttpResponse

urlpatterns = i18n_patterns(
    url(r'^exists/$', lambda r: HttpResponse()),
)
