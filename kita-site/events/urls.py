from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template, redirect_to
from events import views as events_views

urlpatterns = patterns('',
                       url(r'^se/alle/$', events_views.list, name="events_view_all"),
                       url(r'^se/(?P<eventId>[0-9]+)/$', events_views.view, name="events_view"),
                       url(r'^se/(?P<eventId>[0-9]+)/tilmeld/$', events_views.signup, name="events_signup"),
                       url(r'^se/visited/$', events_views.visited, name="events_view_visited"),
)