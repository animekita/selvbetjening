from django.conf.urls.defaults import *
from django.contrib.auth import views as auth_views

import views

urlpatterns = patterns('',
    url(r'^validate/(?P<service>[a-z_0-9]+)/(?P<auth_token>[0-9a-z_]+)/$',
        views.validate,
        name='api_sso_validate'),
    url(r'^info/(?P<service>[a-z_0-9]+)/(?P<auth_token>[0-9a-z_]+)/$',
        views.info,
        name='api_sso_info'),
)