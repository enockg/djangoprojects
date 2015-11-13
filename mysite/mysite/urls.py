"""Urls for the demo of Zinnia"""
import os

from django.contrib import admin
from django.conf.urls import url
from django.conf.urls import include
from django.conf.urls import patterns

from zinnia.sitemaps import TagSitemap
from zinnia.sitemaps import EntrySitemap
from zinnia.sitemaps import CategorySitemap
from zinnia.sitemaps import AuthorSitemap

admin.autodiscover()
handler500 = 'django.views.defaults.server_error'
handler404 = 'django.views.defaults.page_not_found'

urlpatterns = patterns(
    '',
    {'url': '/blog/'}),
      url(r'^blog/', include('zinnia.urls')),
      url(r'^admin/', include(admin.site.urls)),
    )

sitemaps = {'tags': TagSitemap,
            'blog': EntrySitemap,
            'authors': AuthorSitemap,
            'categories': CategorySitemap}

urlpatterns += patterns('django.contrib.sitemaps.views',
                        (r'^sitemap.xml$', 'index',
                         {'sitemaps': sitemaps}),
                        (r'^sitemap-(?P<section>.+)\.xml$', 'sitemap',
                         {'sitemaps': sitemaps}),
                        )

urlpatterns += patterns('django.views.static',
                        url(r'^zinnia/(?P<path>.*)$', 'serve',
                            {'document_root': os.path.join(
                                os.path.dirname(__file__),
                                '..', 'zinnia', 'media', 'zinnia')}),
                        )