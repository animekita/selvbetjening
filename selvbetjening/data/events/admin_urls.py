from django.conf.urls.defaults import url, patterns

import admin_views

urlpatterns = patterns(
    '',
    url(r'^events/event/(?P<event_id>[0-9]+)/statistics/$',
        admin_views.event_statistics,
        name='events_statistics'),
    url(r'^events/event/(?P<event_id>[0-9]+)/options_print/$',
        admin_views.event_options_print,
        name='events_options_print'),
)