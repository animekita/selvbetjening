from django.conf.urls.defaults import url, patterns

import views

urlpatterns = patterns(
    '',
    url(r'^se/alle/$',
        views.list,
        name="events_view_all"),

    url(r'^se/(?P<event_id>[0-9]+)/$',
        views.view,
        name="events_view"),

    url(r'^se/(?P<event_id>[0-9]+)/tilmeld/$',
        views.signup,
        name="events_signup"),

    url(r'^se/(?P<event_id>[0-9]+)/afmeld/$',
        views.signoff,
        name="events_signoff"),

    url(r'^se/(?P<event_id>[0-9]+)/tilvalg/$',
        views.change_options,
        name="events_change_options"),

    url(r'^se/visited/$',
        views.visited,
        name="events_view_visited"),
)