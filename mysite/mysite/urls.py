"""Urls for the demo of Zinnia"""
import os

from django.contrib import admin
from django.conf.urls import url
from django.conf.urls import patterns, include, url
from django.contrib import admin
from mysite.views import hello, current_datetime

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite0.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^hello/$', hello),
    url(r'^time/$', current_datetime),
    url(r'^$', weblog),
	#url(r'^weblog/', include('zinnia.urls')),
	#url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^admin/', include(admin.site.urls)),
)