from django.conf.urls import *
from django.views.generic.base import TemplateView

import views.events

urlpatterns = patterns(
    '',
    url(r'^events/$', views.events.event_list, name='events_list'),
    url(r'^events/(?P<event_pk>[0-9]+)/attendees/$', views.events.event_attendees, name='events_attendees_list'),
    url(r'^events/(?P<event_pk>[0-9]+)/statistics/$', views.events.event_statistics, name='events_statistics'),
    url(r'^events/(?P<event_pk>[0-9]+)/financial/$', views.events.event_financial, name='events_financial'),
    url(r'^events/(?P<event_pk>[0-9]+)/settings/selections/$', views.events.event_settings_selections, name='events_settings_selections'),
    url(r'^events/(?P<event_pk>[0-9]+)/settings/$', views.events.event_settings, name='events_settings'),

    url(r'^$', TemplateView.as_view(template_name='sadmin2/site.html'), name='dashboard'))
