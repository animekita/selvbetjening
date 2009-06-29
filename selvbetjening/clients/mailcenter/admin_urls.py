from django.conf.urls.defaults import *

import admin_views

urlpatterns = patterns('',
    url(r'^mailcenter/mail/(?P<mail_id>[0-9]+)/send/',
        admin_views.send,
        name='mailcenter_send'),
    url(r'^mailcenter/mail/(?P<mail_id>[0-9]+)/send-preview/',
        admin_views.send_preview,
        name='mailcenter_send_preview'),
    url(r'^mailcenter/mail/(?P<mail_id>[0-9]+)/preview/',
        admin_views.preview,
        name='mailcenter_preview'),
)