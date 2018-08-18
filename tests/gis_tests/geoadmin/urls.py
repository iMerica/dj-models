from djmodels.conf.urls import include, url
from djmodels.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
]
