from djmodels.conf.urls import url
from djmodels.conf.urls.i18n import i18n_patterns
from djmodels.utils.translation import gettext_lazy as _
from djmodels.views.generic import TemplateView

view = TemplateView.as_view(template_name='dummy.html')

app_name = 'account'
urlpatterns = i18n_patterns(
    url(_(r'^register/$'), view, name='register'),
)
