
from django.conf.urls import *

import views

urlpatterns = patterns(
    '',
    url(r'^$',
        views.events_list,
        name='eventportal_events'),

    url(r'^(?P<event_pk>[0-9]+)/$',
        views.event_detail,
        name='eventportal_event'),

    url(r'^(?P<event_pk>[0-9]+)/register/$',
        views.event_register,
        name='eventportal_event_register'),

    url(r'^(?P<event_pk>[0-9]+)/unregister/$',
        views.event_unregister,
        name='eventportal_event_unregister'),

    url(r'^(?P<event_pk>[0-9]+)/status/update/$',
        views.event_status_update,
        name='eventportal_event_status_update'),

    url(r'^(?P<event_pk>[0-9]+)/status/$',
        views.event_status,
        name='eventportal_event_status'),

)