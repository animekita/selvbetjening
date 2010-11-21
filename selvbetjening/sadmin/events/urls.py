from django.conf.urls.defaults import patterns, url

url_patterns = patterns('selvbetjening.sadmin.events.views',
    url(r'^$', 'list_events', name='events_list'),

    url(r'^view/(?P<event_id>[0-9]+)/attendees/(?P<attendee_id>[0-9]+)/', 'view_attendee',
        name='events_view_attendee'),
    url(r'^view/(?P<event_id>[0-9]+)/update/', 'update', name='events_update'),
    url(r'^view/(?P<event_id>[0-9]+)/attendees/', 'view_attendees', name='events_view_attendees'),
    url(r'^view/(?P<event_id>[0-9]+)/statistics/', 'view_statistics', name='events_view_statistics'),
    url(r'^view/(?P<event_id>[0-9]+)/', 'view', name='events_view'),

    url(r'^create/', 'create', name='events_create'),

    url(r'^ajax/search/attendees/(?P<event_id>[0-9]+)/',
        'ajax_attendee_search', name='events_ajax_attendee_search'),
    url(r'^ajax/search/', 'ajax_search', name='events_ajax_search'),
)