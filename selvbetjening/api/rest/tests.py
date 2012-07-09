import simplejson

from django.test import TestCase
from django.test.client import Client

from selvbetjening.core.events.tests import Database as EventDatabase

class EventsAPITest(TestCase):

    def test_attendees_nonexisting(self):
        c = Client()
        response = c.get('/api/rest/v1/attendee/')
        content = simplejson.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['objects'], [])

    def test_event_attendees(self):
        event = EventDatabase.new_event()
        user = EventDatabase.new_user()
        user.first_name = 'John'
        user.last_name = 'Doe'
        user.save()

        EventDatabase.attend(user, event)

        c = Client()
        response = c.get('/api/rest/v1/attendee/')
        content = simplejson.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(content['objects'], [])



