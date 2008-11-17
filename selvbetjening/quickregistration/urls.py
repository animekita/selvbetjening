from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

from views import register

urlpatterns = patterns('',
    url(r'^$', register, name='quickrregistration_register'),
    url(r'^velkommen/$', direct_to_template,
        {'template': 'registration/welcome.html'}, name='quickregistration_complete')
)