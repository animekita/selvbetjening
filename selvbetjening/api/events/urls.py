from django.conf.urls.defaults import *
from piston.resource import Resource

from handlers import AttendeeHandler

attendee_handler = Resource(AttendeeHandler)

urlpatterns = patterns('',
   url(r'^(?P<event_pk>[0-9]+)/attendee/(?P<attendee_pk>[0-9]+)/', attendee_handler),
   url(r'^(?P<event_pk>[0-9]+)/attendees/', attendee_handler),
)