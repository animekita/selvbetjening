
from django.conf.urls import *

import views

urlpatterns = patterns('',

    # User registration

     url(r'^registration/$', views.register,
         kwargs={
             'login_on_success': True,
             'success_page': 'userportal_edit_profile'
         },
         name='userportal_register'),

    # Edit profile

    url(r'^update/$', views.edit_profile,
        name='userportal_edit_profile'),

    url(r'^update/picture/$', views.edit_picture,
        name='userportal_edit_picture'),

    url(r'^update/privacy/$', views.edit_privacy,
        name='userportal_edit_privacy'),

    url(r'^update/username/$', views.edit_username,
        name='userportal_edit_username'),

    url(r'^update/password/$', views.edit_password,
        name='userportal_edit_password'),

    # Public profiles

    url(r'^vis/(?P<username>[0-9a-zA-Z_\-]+)/$', views.public_profile_page,
        name='userportal_public_profile'),

    # Profile landing page

    url(r'^', views.profile, name='userportal_profile'),



)