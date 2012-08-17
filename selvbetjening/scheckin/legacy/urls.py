from django.conf.urls import *

import views

urlpatterns = patterns('',
    url(r'^(?P<event_id>[0-9]+)/$', views.checkin),
)
