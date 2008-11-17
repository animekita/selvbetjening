from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    url(r'^(?P<cinema_name>.+)/reservation/$',
        views.create_booking,
        name='booking_create_booking'),

    url(r'^(?P<cinema_name>.+)/$',
        views.view_cinema,
        name='booking_view_cinema'),
)