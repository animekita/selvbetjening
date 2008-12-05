from django.conf.urls.defaults import patterns, url
from django.contrib.auth import views as auth_views

from views import profile_edit, profile_change_email, \
     profile_change_email_confirm, password_change

urlpatterns = patterns('',
    url(r'^rediger/$', profile_edit,
        name='members_editprofile'),

    url(r'^login/$', auth_views.login,
        {'template_name': 'members/login.html'},
        name='members_login'),

    url(r'^logud/$', auth_views.logout,
        {'template_name': 'members/logout.html'},
        name='members_logout'),

    url(r'^nulstil-kodeord/$', auth_views.password_reset,
        {'template_name':'members/password_reset.html'}, name='auth_password_reset'),
    url(r'^nulstil-kodeord/email-sendt/$', auth_views.password_reset_done,
        {'template_name':'members/password_reset_done.html'},
        name='members_password_reset_done'),
    url(r'^nulstil-kodeord/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/', auth_views.password_reset_confirm,
        name='auth_password_reset_confirm'),
    url(r'^nulstil-kodeord/reset/done/$', auth_views.password_reset_complete),

    url(r'^skift-kodeord/$', password_change,
        name='members_password_change'),
    url(r'^skift-kodeord/done/$', auth_views.password_change_done,
        {'template_name':'members/password_change_done.html'}, name='auth_password_change_done'),

    url(r'^skift-email/$', profile_change_email,
        name='members_change_email'),
    url(r'^skift-email/confirm/(?P<key>\w+)/$', profile_change_email_confirm,
        name='members_change_email_confirm'),
)