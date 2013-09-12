from django.conf.urls import *
from django.views.generic.base import TemplateView
from django.contrib.auth import views as auth_views

from selvbetjening.sadmin2.decorators import sadmin_prerequisites
from selvbetjening.portal.profile.forms import LoginForm

import views.events

urlpatterns = patterns(
    '',
    url(r'^events/$', views.events.event_list, name='events_list'),
    url(r'^events/create/$', views.events.event_create, name='events_create'),
    url(r'^events/(?P<event_pk>[0-9]+)/attendees/$', views.events.event_attendees, name='events_attendees_list'),
    url(r'^events/(?P<event_pk>[0-9]+)/statistics/$', views.events.event_statistics, name='events_statistics'),
    url(r'^events/(?P<event_pk>[0-9]+)/financial/$', views.events.event_financial, name='events_financial'),
    url(r'^events/(?P<event_pk>[0-9]+)/settings/selections/$', views.events.event_settings_selections, name='events_settings_selections'),
    url(r'^events/(?P<event_pk>[0-9]+)/settings/$', views.events.event_settings, name='events_settings'),

    url(r'^login/$', auth_views.login, name='login', kwargs=
        {
            'template_name': 'sadmin2/login.html',
            'authentication_form': LoginForm
        }),

    url(r'^$', sadmin_prerequisites(TemplateView.as_view(template_name='sadmin2/site.html')), name='dashboard'))
