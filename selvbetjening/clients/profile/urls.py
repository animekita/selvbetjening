from django.conf.urls.defaults import *
from django.contrib.auth import views as auth_views
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required

from views import profile_edit, password_change, current_events, profile_page,\
     picture_edit

import forms

urlpatterns = patterns('',
    url(r'^opdater/billede/$', picture_edit,
        name='members_editpicture'),

    url(r'^opdater/$', profile_edit,
        name='members_editprofile'),

    url(r'^login/$', auth_views.login,
        {'template_name': 'profile/login.html', 'authentication_form': forms.LoginForm},
        name='members_login'),

    url(r'^logud/$', auth_views.logout,
        {'template_name': 'profile/logout.html'},
        name='members_logout'),

    url(r'^nulstil-kodeord/$', auth_views.password_reset,
        {'template_name':'profile/password_reset.html',
         'email_template_name':'profile/password_reset_email.html'}, name='auth_password_reset'),
    url(r'^nulstil-kodeord/email-sendt/$', auth_views.password_reset_done,
        {'template_name':'profile/password_reset_done.html'},
        name='members_password_reset_done'),
    url(r'^nulstil-kodeord/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/', auth_views.password_reset_confirm,
        {'template_name':'profile/password_reset_confirm.html'},
        name='auth_password_reset_confirm'),
    url(r'^nulstil-kodeord/reset/done/$', auth_views.password_reset_complete,
        {'template_name':'profile/password_reset_complete.html'}),

    url(r'^skift-kodeord/$', password_change,
        name='members_password_change'),
    url(r'^skift-kodeord/done/$', auth_views.password_change_done,
        {'template_name':'profile/password_change_done.html'}, name='auth_password_change_done'),

    url(r'^arrangementer/', current_events, name='members_current_events'),

    url(r'^', profile_page, name='members_profile'),
)