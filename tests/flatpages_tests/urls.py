from djmodels.conf.urls import include, url
from djmodels.contrib.flatpages.sitemaps import FlatPageSitemap
from djmodels.contrib.sitemaps import views

# special urls for flatpage test cases
urlpatterns = [
    url(r'^flatpages/sitemap\.xml$', views.sitemap,
        {'sitemaps': {'flatpages': FlatPageSitemap}},
        name='djmodels.contrib.sitemaps.views.sitemap'),

    url(r'^flatpage_root', include('djmodels.contrib.flatpages.urls')),
    url(r'^accounts/', include('djmodels.contrib.auth.urls')),
]
