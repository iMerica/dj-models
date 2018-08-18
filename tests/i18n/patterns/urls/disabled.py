from djmodels.conf.urls import url
from djmodels.conf.urls.i18n import i18n_patterns
from djmodels.views.generic import TemplateView

view = TemplateView.as_view(template_name='dummy.html')

urlpatterns = i18n_patterns(
    url(r'^prefixed/$', view, name='prefixed'),
)
