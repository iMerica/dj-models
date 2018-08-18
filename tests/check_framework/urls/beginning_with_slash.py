from djmodels.conf.urls import url
from djmodels.urls import path

urlpatterns = [
    path('/path-starting-with-slash/', lambda x: x),
    url(r'/url-starting-with-slash/$', lambda x: x),
]
