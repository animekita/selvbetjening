from django.conf.urls import *
from django.views.generic import TemplateView

from views import register

urlpatterns = patterns('',
    url(r'^$', register, name='quickregistration_register'),
    url(r'^velkommen/$', TemplateView.as_view(template_name='quickregistration/welcome.html'),
        name='quickregistration_complete')
)