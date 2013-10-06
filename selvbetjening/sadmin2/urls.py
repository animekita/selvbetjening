from django.conf.urls import *
from django.views.generic.base import TemplateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm

from selvbetjening.sadmin2.decorators import sadmin_prerequisites

import views.events
import views.event
import views.users
import views.user

urlpatterns = patterns(
    '',

    url(r'userportal/$', views.users.users_list, name='users_list'),
    url(r'userportal/create/$', views.users.users_create, name='users_create'),

    url(r'userportal/groups/$', views.users.users_groups_list, name='users_groups_list'),
    url(r'userportal/groups/create/$', views.users.users_groups_create, name='users_groups_create'),

    url(r'userportal/groups/(?P<group_pk>[0-9]+)/$', views.users.users_group, name='users_group'),

    url(r'userportal/reports/age/$', views.users.users_reports_age, name='users_reports_age'),
    url(r'userportal/reports/address/$', views.users.users_reports_address, name='users_reports_address'),

    url(r'userportal/(?P<user_pk>[0-9]+)/$', views.user.user_change, name='user'),
    url(r'userportal/(?P<user_pk>[0-9]+)/password/$', views.user.user_password, name='user_password'),

    url(r'^events/$', views.events.event_list, name='events_list'),
    url(r'^events/create/$', views.events.event_create, name='events_create'),
    url(r'^events/register-payments/$', views.events.register_payments, name='events_register_payments'),

    url(r'^events/(?P<event_pk>[0-9]+)/$', views.event.event_overview, name='event_overview'),
    url(r'^events/(?P<event_pk>[0-9]+)/attendees/$', views.event.event_attendees, name='event_attendees'),
    url(r'^events/(?P<event_pk>[0-9]+)/attendees/(?P<attendee_pk>[0-9]+)/$', views.event.event_attendee, name='event_attendee'),
    url(r'^events/(?P<event_pk>[0-9]+)/attendees/(?P<attendee_pk>[0-9]+)/payments/$', views.event.event_attendee_payments, name='event_attendee_payments'),
    url(r'^events/(?P<event_pk>[0-9]+)/attendees/(?P<attendee_pk>[0-9]+)/selections/$', views.event.event_attendee_selections, name='event_attendee_selections'),
    url(r'^events/(?P<event_pk>[0-9]+)/attendees/(?P<attendee_pk>[0-9]+)/notes/$', views.event.event_attendee_notes, name='event_attendee_notes'),
    url(r'^events/(?P<event_pk>[0-9]+)/attendees/add/$', views.event.event_attendees_add, name='event_attendees_add'),

    url(r'^events/(?P<event_pk>[0-9]+)/selections/$', views.event.event_selections, name='event_selections'),
    url(r'^events/(?P<event_pk>[0-9]+)/selections/manage/$', views.event.event_selections_manage, name='event_selections_manage'),

    url(r'^events/(?P<event_pk>[0-9]+)/selections/group/create/$', views.event.event_selections_create_group, name='event_selections_create_group'),
    url(r'^events/(?P<event_pk>[0-9]+)/selections/group/(?P<group_pk>[0-9]+)/$', views.event.event_selections_edit_group, name='event_selections_edit_group'),

    url(r'^events/(?P<event_pk>[0-9]+)/selections/group/(?P<group_pk>[0-9]+)/options/create/$', views.event.event_selections_create_option, name='event_selections_create_option'),
    url(r'^events/(?P<event_pk>[0-9]+)/selections/group/(?P<group_pk>[0-9]+)/options/(?P<option_pk>[0-9]+)/$', views.event.event_selections_edit_option, name='event_selections_edit_option'),

    url(r'^events/(?P<event_pk>[0-9]+)/account/$', views.event.event_account, name='event_account'),
    url(r'^events/(?P<event_pk>[0-9]+)/settings/$', views.event.event_settings, name='event_settings'),
    url(r'^events/(?P<event_pk>[0-9]+)/reports/checkin/$', views.event.report_check_in, name='event_report_check_in'),
    url(r'^events/(?P<event_pk>[0-9]+)/reports/registration/$', views.event.report_registration, name='event_report_registration'),

    url(r'^login/$', auth_views.login, name='login', kwargs=
        {
            'template_name': 'sadmin2/login.html',
            'authentication_form': AuthenticationForm
        }),

    url(r'^logout/$', auth_views.logout_then_login, name='logout', kwargs=
        {
            'login_url': 'sadmin2:login'
        }),

    url(r'^$', sadmin_prerequisites(TemplateView.as_view(template_name='sadmin2/dashboard.html')), name='dashboard',
        kwargs={'sadmin2_breadcrumbs_active': 'dashboard'}))
