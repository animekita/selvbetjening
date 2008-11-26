from django.conf.urls.defaults import patterns, url
from django.contrib.auth import views as auth_views

from views import profile_edit, profile_change_email, \
     profile_change_email_confirm

urlpatterns = patterns('',
    url(r'^rediger/$',
        profile_edit,
        name='members_editprofile'),

    url(r'^skift-email/$',
        profile_change_email,
        name='members_change_email'),

    url(r'^skift-email/confirm/(?P<key>\w+)/$',
        profile_change_email_confirm,
        name='members_change_email_confirm'),
)