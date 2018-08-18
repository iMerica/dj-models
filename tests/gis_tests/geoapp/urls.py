from djmodels.conf.urls import url
from djmodels.contrib.gis import views as gis_views
from djmodels.contrib.gis.sitemaps import views as gis_sitemap_views
from djmodels.contrib.sitemaps import views as sitemap_views

from .feeds import feed_dict
from .sitemaps import sitemaps

urlpatterns = [
    url(r'^feeds/(?P<url>.*)/$', gis_views.feed, {'feed_dict': feed_dict}),
]

urlpatterns += [
    url(r'^sitemaps/(?P<section>\w+)\.xml$', sitemap_views.sitemap, {'sitemaps': sitemaps}),
]

urlpatterns += [
    url(r'^sitemaps/kml/(?P<label>\w+)/(?P<model>\w+)/(?P<field_name>\w+)\.kml$',
        gis_sitemap_views.kml,
        name='djmodels.contrib.gis.sitemaps.views.kml'),
    url(r'^sitemaps/kml/(?P<label>\w+)/(?P<model>\w+)/(?P<field_name>\w+)\.kmz$',
        gis_sitemap_views.kmz,
        name='djmodels.contrib.gis.sitemaps.views.kmz'),
]
