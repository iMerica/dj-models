from djmodels.conf.urls import url
from djmodels.urls import path
from djmodels.utils.translation import gettext_lazy as _
from djmodels.views.generic import TemplateView

view = TemplateView.as_view(template_name='dummy.html')

app_name = 'account'
urlpatterns = [
    url(_(r'^register/$'), view, name='register'),
    url(_(r'^register-without-slash$'), view, name='register-without-slash'),
    path(_('register-as-path/'), view, name='register-as-path'),
]
