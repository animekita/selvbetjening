from django.conf.urls.defaults import *

import views

urlpatterns = patterns(
    '',
    url(r'^se/alle/$',
        views.list_events,
        name='eventregistration_view_all'),

    url(r'^se/(?P<event_id>[0-9]+)/$',
        views.view,
        name='eventregistration_view'),

    url(r'^se/(?P<event_id>[0-9]+)/tilmeld/$',
        views.signup,
        name='eventregistration_signup'),

    url(r'^se/(?P<event_id>[0-9]+)/afmeld/$',
        views.signoff,
        name='eventregistration_signoff'),

    url(r'^se/(?P<event_id>[0-9]+)/tilvalg/$',
        views.change_options,
        name='eventregistration_change_options'),

    url(r'^se/(?P<event_id>[0-9]+)/kvittering/$',
        views.view_invoice,
        name='eventregistration_view_invoice'),

)