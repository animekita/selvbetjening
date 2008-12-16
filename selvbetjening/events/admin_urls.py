from django.conf.urls.defaults import url, patterns

import views
import admin_views

urlpatterns = patterns(
    '',
    url(r'^events/event/(?P<event_id>[0-9]+)/statistics/$',
        admin_views.event_statistics,
        name='events_statistics'),
)