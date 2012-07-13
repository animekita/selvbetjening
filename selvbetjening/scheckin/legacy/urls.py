from django.conf.urls import *

import views

urlpatterns = patterns('',
    url(r'^$', views.checkin),
)
