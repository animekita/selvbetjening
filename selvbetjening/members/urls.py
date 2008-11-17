from django.conf.urls.defaults import *
from django.contrib.auth import views as auth_views

from views import profile, profile_edit, profile_change_email,\
     profile_change_email_confirm, password_change

urlpatterns = patterns('',
    url(r'^$',
        profile,
        name='members_profile'),

    url(r'^rediger/$',
        profile_edit,
        name='members_editprofile'),

    url(r'^skift-email/$',
        profile_change_email,
        name='members_change_email'),

    url(r'^skift-email/confirm/(?P<key>\w+)/$',
        profile_change_email_confirm,
        name='members_change_email_confirm'),

    url(r'^skift-kodeord/$',
        password_change,
        {'template_name': 'members/changePassword.html'},
        name='auth_password_change'),

    url(r'^skift-kodeord/done/$',
        auth_views.password_change_done,
        {'template_name': 'members/changePasswordDone.html'},
        name='auth_password_change_done'),
)