
from django.conf.urls import *

import views

urlpatterns = patterns(
    '',

    url(r'^registration/(?P<event_pk>[0-9]+)/$',
        views.step_controller,
        name='eventsingle_steps'),

    url(r'^registration/(?P<event_pk>[0-9]+)/step1/$',
        views.step1,
        name='eventsingle_step1'),

    url(r'^registration/(?P<event_pk>[0-9]+)/step2/$',
        views.step2,
        name='eventsingle_step2')
)
