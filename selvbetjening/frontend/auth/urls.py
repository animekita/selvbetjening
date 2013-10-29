from django.conf.urls import *
from django.contrib.auth import views as auth_views

import forms

urlpatterns = patterns('',

    url(r'^log-in/$', auth_views.login,
        {
            'template_name': 'auth/login.html',
            'authentication_form': forms.AuthenticationForm
        },
        name='auth_login'),

    url(r'^log-out/$', auth_views.logout,
        {
            'template_name': 'auth/logout.html'
        },
        name='auth_logout'),

    url(r'^reset-password/$', auth_views.password_reset,
        {
            'template_name': 'auth/password_reset/password_reset.html',
            'password_reset_form': forms.PasswordResetForm,
            'email_template_name':'auth/password_reset/password_reset_email.html'
        },
        name='auth_password_reset'),

    url(r'^reset-password/email-sendt/$', auth_views.password_reset_done,
        {
            'template_name': 'auth/password_reset/password_reset_done.html'
        },
        name='members_password_reset_done'),

    url(r'^reset-password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/', auth_views.password_reset_confirm,
        {
            'template_name': 'auth/password_reset/password_reset_confirm.html',
            'set_password_form': forms.SetPasswordForm
        },
        name='auth_password_reset_confirm'),

    url(r'^reset-password/reset/done/$', auth_views.password_reset_complete,
        {''
         'template_name': 'auth/password_reset/password_reset_complete.html'
        })
)