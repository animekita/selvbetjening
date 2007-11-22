from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from registration.views import activate, register

urlpatterns = patterns('',  
    url(r'^$',
        register,
        name='registration_register'),
    
    url(r'^email-sendt/$',
        direct_to_template,
        {'template': 'registration/registration_complete.html'},
        name='registration_complete'),
    
    url(r'^aktiver/(?P<activation_key>\w+)/$',
        activate,
        name='registration_activate'),
)