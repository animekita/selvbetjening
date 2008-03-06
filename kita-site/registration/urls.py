from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from registration.views import activate, register, create_and_signup

urlpatterns = patterns('',  
    url(r'^$',
        register,
        name='registration_register'),

     url(r'^direct/$',
        create_and_signup,
        name='registration_create_and_signup'),       
        
    url(r'^email-sendt/$',
        direct_to_template,
        {'template': 'registration/registration_complete.html'},
        name='registration_complete'),
    
    url(r'^aktiver/(?P<activation_key>\w+)/$',
        activate,
        name='registration_activate'),
)