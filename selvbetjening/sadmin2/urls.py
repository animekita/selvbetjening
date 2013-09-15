from django.conf.urls import *
from django.views.generic.base import TemplateView
from django.contrib.auth import views as auth_views

from selvbetjening.sadmin2.decorators import sadmin_prerequisites
from selvbetjening.portal.profile.forms import LoginForm

import views.events
import views.event

urlpatterns = patterns(
    '',
    url(r'^events/$', views.events.event_list, name='events_list'),
    url(r'^events/ajax/$', views.events.event_list, name='events_list_ajax', kwargs={'ajax': True}),
    url(r'^events/create/$', views.events.event_create, name='events_create'),

    url(r'^events/(?P<event_pk>[0-9]+)/$', views.event.event_attendees, name='event_attendees'),
    url(r'^events/(?P<event_pk>[0-9]+)/ajax/$', views.event.event_attendees, name='event_attendees_ajax', kwargs={'ajax': True}),
    url(r'^events/(?P<event_pk>[0-9]+)/statistics/$', views.event.event_statistics, name='event_statistics'),
    url(r'^events/(?P<event_pk>[0-9]+)/account/$', views.event.event_account, name='event_account'),
    url(r'^events/(?P<event_pk>[0-9]+)/settings/selections/$', views.event.event_settings_selections, name='event_settings_selections'),
    url(r'^events/(?P<event_pk>[0-9]+)/settings/$', views.event.event_settings, name='event_settings'),

    url(r'^login/$', auth_views.login, name='login', kwargs=
        {
            'template_name': 'sadmin2/login.html',
            'authentication_form': LoginForm
        }),

    url(r'^$', sadmin_prerequisites(TemplateView.as_view(template_name='sadmin2/dashboard.html')), name='dashboard',
        kwargs={'sadmin2_breadcrumbs_active': 'dashboard'}))
