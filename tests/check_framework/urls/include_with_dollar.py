from djmodels.conf.urls import include, url

urlpatterns = [
    url(r'^include-with-dollar$', include([])),
]
