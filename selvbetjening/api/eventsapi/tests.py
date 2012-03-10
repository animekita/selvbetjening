import simplejson

from django.test import TestCase
from django.test.client import Client

from selvbetjening.core.events.tests import Database as EventDatabase

class EventsAPITest(TestCase):

    def test_event_nonexisting(self):
        c = Client()
        response = c.get('/api/events/1000/attendees/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '[]')

    def test_event_attendees(self):
        event = EventDatabase.new_event()
        user = EventDatabase.new_user()
        user.first_name = 'John'
        user.last_name = 'Doe'
        user.save()

        EventDatabase.attend(user, event)

        c = Client()
        response = c.get('/api/events/%s/attendees/' % event.pk)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.content, '[]')

        attendees = simplejson.loads(response.content)

        self.assertEqual(len(attendees), 1)
        attendee = attendees[0]

        self.assertEqual(attendee['user']['username'], user.username)

        response = c.get('/api/events/%s/attendees/?q=Jane' % event.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '[]')

        response = c.get('/api/events/%s/attendees/?q=John' % event.pk)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.content, '[]')



