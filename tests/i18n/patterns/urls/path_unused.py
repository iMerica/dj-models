from djmodels.conf.urls import url
from djmodels.views.generic import TemplateView

view = TemplateView.as_view(template_name='dummy.html')

urlpatterns = [
    url(r'^nl/foo/', view, name='not-translated'),
]
