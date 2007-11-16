"""
URLConf for Django user registration.

Recommended usage is to use a call to ``include()`` in your project's
root URLConf to include this URLConf for any URL beginning with
'/accounts/'.

"""


from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib.auth import views as auth_views


from members.views import activate, register, profile, profile_edit, profile_change_email, profile_change_email_confirm, password_change


urlpatterns = patterns('',  
    url(r'^login/$',
        auth_views.login,
        {'template_name': 'registration/login.html'},
        name='auth_login'),
    
    url(r'^logud/$',
        auth_views.logout,
        {'template_name': 'registration/logout.html'},
        name='auth_logout'),
    
    url(r'^profile/skift-kodeord/$',
        password_change,
        {'template_name': 'registration/changePassword.html'},
        name='auth_password_change'),
    
    url(r'^profil/skift-kodeord/done/$',
        auth_views.password_change_done,
        {'template_name': 'registration/changePasswordDone.html'},
        name='auth_password_change_done'),
    
    url(r'^nulstil-kodeord/$',
        auth_views.password_reset,
        {'template_name':'registration/resetPassword.html'},
        name='auth_password_reset'),
    
    url(r'^nulstil-kodeord/done/$',
        auth_views.password_reset_done,
        {'template_name':'registration/resetPasswordDone.html'},
        name='auth_password_reset_done'),
    
    url(r'^bliv-medlem/$',
        register,
        name='registration_register'),
    
    url(r'^bliv-medlem/email-sendt/$',
        direct_to_template,
        {'template': 'registration/registration_complete.html'},
        name='registration_complete'),
    
    url(r'^bliv-medlem/aktiver/(?P<activation_key>\w+)/$',
        activate,
        name='registration_activate'),
    
    url(r'^profil/$',
        profile,
        name='members_profile'),
    
    url(r'^profil/rediger/$',
        profile_edit,
        name='members_editprofile'),
    
    url(r'^profil/skift-email/$',
        profile_change_email,
        name='members_change_email'),
    
    url(r'^profil/skift-email/confirm/(?P<key>\w+)/$', 
        profile_change_email_confirm, 
        name='members_change_email_confirm')
)