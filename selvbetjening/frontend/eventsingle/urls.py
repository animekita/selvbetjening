
from django.conf.urls import *

import views

urlpatterns = patterns(
    '',

    url(r'^registration/(?P<event_pk>[0-9]+)/$',
        views.step_controller,
        name='eventsingle_steps')
)
