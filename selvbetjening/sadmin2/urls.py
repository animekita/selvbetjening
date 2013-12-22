from django.conf.urls import *
from django.views.generic.base import TemplateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm

from selvbetjening.sadmin2.decorators import sadmin_prerequisites

import views.events
import views.event
import views.users
import views.user
import views.emails
import views.autocomplete
import views.options

urlpatterns = patterns(
    '',


    # Users

    # TODO we are not using the _list postfix consistently
    url(r'^users/$',
        views.users.users_list,
        name='users_list'),
    url(r'^users/create/$',
        views.users.users_create,
        name='users_create'),

    url(r'^users/(?P<user_pk>[0-9]+)/$',
        views.user.user_change,
        name='user'),
    url(r'^users/(?P<user_pk>[0-9]+)/password/$',
        views.user.user_password,
        name='user_password'),


    url(r'^users/groups/$',
        views.users.users_groups_list,
        name='users_groups_list'),
    url(r'^users/groups/create/$',
        views.users.users_groups_create,
        name='users_groups_create'),

    url(r'^users/groups/(?P<group_pk>[0-9]+)/$',
        views.users.users_group,
        name='users_group'),

    url(r'^users/reports/age/$',
        views.users.users_reports_age,
        name='users_reports_age'),
    url(r'^users/reports/address/$',
        views.users.users_reports_address,
        name='users_reports_address'),


    # Events

    url(r'^events/$',
        views.events.event_list,
        name='events_list'),
    url(r'^events/create/$',
        views.events.event_create,
        name='events_create'),
    url(r'^events/register-payments/$',
        views.events.register_payments,
        name='events_register_payments'),

    url(r'^events/(?P<event_pk>[0-9]+)/$',
        views.event.event_overview,
        name='event_overview'),

    url(r'^events/(?P<event_pk>[0-9]+)/attendees/$',
        views.event.event_attendees,
        name='event_attendees'),
    url(r'^events/(?P<event_pk>[0-9]+)/attendees/add/$',
        views.event.event_attendees_add,
        name='event_attendees_add'),

    url(r'^events/(?P<event_pk>[0-9]+)/attendees/(?P<attendee_pk>[0-9]+)/$',
        views.event.event_attendee,
        name='event_attendee'),
    url(r'^events/(?P<event_pk>[0-9]+)/attendees/(?P<attendee_pk>[0-9]+)/payments/$',
        views.event.event_attendee_payments,
        name='event_attendee_payments'),
    url(r'^events/(?P<event_pk>[0-9]+)/attendees/(?P<attendee_pk>[0-9]+)/selections/$',
        views.event.event_attendee_selections,
        name='event_attendee_selections'),
    url(r'^events/(?P<event_pk>[0-9]+)/attendees/(?P<attendee_pk>[0-9]+)/notes/$',
        views.event.event_attendee_notes,
        name='event_attendee_notes'),
    url(r'^events/(?P<event_pk>[0-9]+)/attendees/(?P<attendee_pk>[0-9]+)/delete/$',
        views.event.event_attendee_delete,
        name='event_attendee_delete'),

    url(r'^events/(?P<event_pk>[0-9]+)/selections/$',
        views.options.event_selections,
        name='event_selections'),
    url(r'^events/(?P<event_pk>[0-9]+)/selections/transfer/$',
        views.options.event_selections_transfer,
        name='event_selections_transfer'),

    url(r'^events/(?P<event_pk>[0-9]+)/selections/group/create/$',
        views.options.event_selections_create_group,
        name='event_selections_create_group'),
    url(r'^events/(?P<event_pk>[0-9]+)/selections/group/(?P<group_pk>[0-9]+)/$',
        views.options.event_selections_edit_group,
        name='event_selections_edit_group'),

    url(r'^events/(?P<event_pk>[0-9]+)/selections/group/(?P<group_pk>[0-9]+)/options/create/$',
        views.options.event_selections_create_option,
        name='event_selections_create_option'),
    url(r'^events/(?P<event_pk>[0-9]+)/selections/group/(?P<group_pk>[0-9]+)/options/create/(?P<type_raw>[a-z]+)/$',
        views.options.event_selections_create_option_step2,
        name='event_selections_create_option_step2'),
    url(r'^events/(?P<event_pk>[0-9]+)/selections/group/(?P<group_pk>[0-9]+)/options/(?P<option_pk>[0-9]+)/delete/$',
        views.options.event_selections_delete_option,
        name='event_selections_delete_option'),
    url(r'^events/(?P<event_pk>[0-9]+)/selections/group/(?P<group_pk>[0-9]+)/options/(?P<option_pk>[0-9]+)/$',
        views.options.event_selections_edit_option,
        name='event_selections_edit_option'),

    url(r'^events/(?P<event_pk>[0-9]+)/account/$',
        views.event.event_account,
        name='event_account'),
    url(r'^events/(?P<event_pk>[0-9]+)/settings/$',
        views.event.event_settings,
        name='event_settings'),
    url(r'^events/(?P<event_pk>[0-9]+)/settings/selections/$',
        views.options.event_selections_manage,
        name='event_settings_selections'),
    url(r'^events/(?P<event_pk>[0-9]+)/reports/checkin/$',
        views.event.report_check_in,
        name='event_report_check_in'),
    url(r'^events/(?P<event_pk>[0-9]+)/reports/registration/$',
        views.event.report_registration,
        name='event_report_registration'),
    url(r'^events/(?P<event_pk>[0-9]+)/reports/age/$',
        views.event.report_age,
        name='event_report_age'),
    url(r'^events/(?P<event_pk>[0-9]+)/reports/address/$',
        views.event.report_address,
        name='event_report_address'),

    # E-mails

    url(r'^emails/queue/$',
        views.emails.queue,
        name='emails_queue'),

    url(r'^emails/templates/$',
        views.emails.templates,
        name='emails_templates'),
    url(r'^emails/templates/create/$',
        views.emails.templates_create,
        name='emails_templates_create'),

    url(r'^emails/templates/(?P<template_pk>[0-9]+)/$',
        views.emails.template,
        name='emails_template'),
    url(r'^emails/templates/(?P<template_pk>[0-9]+)/preview/$',
        views.emails.template_preview,
        name='emails_template_preview'),
    url(r'^emails/templates/(?P<template_pk>[0-9]+)/send/$',
        views.emails.template_send,
        name='emails_template_send'),
    url(r'^emails/templates/(?P<template_pk>[0-9]+)/newsletter/users/$',
        views.emails.template_newsletter_users,
        name='emails_template_newsletter_users'),
    url(r'^emails/templates/(?P<template_pk>[0-9]+)/newsletter/attendees/$',
        views.emails.template_newsletter_attendees,
        name='emails_template_newsletter_attendees'),
    url(r'^emails/templates/(?P<template_pk>[0-9]+)/newsletter/attendees/(?P<event_pk>[0-9]+)$',
        views.emails.template_newsletter_attendees_step2,
        name='emails_template_newsletter_attendees_step2'),
    url(r'^emails/templates/(?P<template_pk>[0-9]+)/newsletter/attendees/(?P<event_pk>[0-9]+)/confirm/$',
        views.emails.template_newsletter_attendees_step3,
        name='emails_template_newsletter_attendees_step3'),

    url(r'autocomplete/users/',
        views.autocomplete.users,
        name='autocomplete_users'),
    url(r'autocomplete/attendees/',
        views.autocomplete.attendees,
        name='autocomplete_attendees'),


    # Auth

    url(r'^login/$', auth_views.login, name='login', kwargs=
        {
            'template_name': 'sadmin2/login.html',
            'authentication_form': AuthenticationForm
        }),

    url(r'^logout/$', auth_views.logout_then_login, name='logout', kwargs=
        {
            'login_url': 'sadmin2:login'
        }),


    # Dashboard

    url(r'^$', sadmin_prerequisites(TemplateView.as_view(template_name='sadmin2/dashboard.html')), name='dashboard',
        kwargs={'sadmin2_breadcrumbs_active': 'dashboard'}))
