from django.conf.urls.defaults import *
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    #Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^simplecontent/', include('django_simplecontent.urls')),
    (r'^tinymce/', include('tinymce.urls')),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
)

if settings.DEBUG:
	urlpatterns += patterns("django.views",
		url(r"%s(?P<path>.*)/?$" % settings.MEDIA_URL[1:], "static.serve", {
			"document_root": settings.MEDIA_ROOT,
		})
	)
