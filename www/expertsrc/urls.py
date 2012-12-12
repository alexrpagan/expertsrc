from django.conf.urls.defaults import *
from django.conf import settings
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

if settings.ALT_ROOT:
    alt_root = ''.join([settings.ALT_ROOT, '/'])

urlpatterns = patterns('',
    (r'%s' % alt_root, include('ui.urls')),
)
