from django.conf.urls.defaults import *

urlpatterns = patterns('django_simplecontent.views',
	(r'^templates/list/$', 'template_list'),
	(r'^templates/edit/(?P<path>\d+)/(?P<template>.+)/$', 'template_edit'),
	(r'^content/list/$', 'content_list'),
	(r'^content/edit/$', 'content_edit'),
	(r'^content/add/$', 'content_add'),
)
