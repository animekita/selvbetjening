from django.core.urlresolvers import reverse
from django.test import TestCase

from selvbetjening.core.events.models import Event, Attend


class EventsTestCase(TestCase):

    fixtures = ['sdemo-example-site.json']

    def setUp(self):
        self.client.login(username='admin', password='admin')

    def test_events(self):
        response = self.client.get(reverse('sadmin2:events_list'))
        self.assertEqual(response.status_code, 200)

    def test_events_create(self):
        url = reverse('sadmin2:events_create')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {
            'title': 'Event 1',
            'move_to_accepted_policy': 'always',
            'maximum_attendees': 0
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Event.objects.filter(title='Event 1').exists())

    def test_events_register_payments(self):
        url = reverse('sadmin2:events_register_payments')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {
            'payment_key': 'EUA.1.2.1',
            'payment': 100
        }, follow=True)

        self.assertEqual(response.status_code, 200)

        attendee = Attend.objects.get(pk=1)  # user1 attendance to Simple Event
        self.assertEqual(attendee.paid, 100)

