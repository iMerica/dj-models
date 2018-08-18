from djmodels.conf.urls import url
from djmodels.contrib.contenttypes import views

urlpatterns = [
    url(r'^shortcut/([0-9]+)/(.*)/$', views.shortcut),
]
