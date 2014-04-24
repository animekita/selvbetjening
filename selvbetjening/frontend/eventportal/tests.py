from django.core.urlresolvers import reverse
from django.test import TestCase
from selvbetjening.core.events.models import Event, Attend, AttendState


class EventPortalTestCase(TestCase):

    fixtures = ['sdemo-example-site.json']

    def setUp(self):
        self.client.login(username='admin', password='admin')

    def test_remove_registration_forbidden(self):

        response = self.client.get(reverse('eventportal_event_unregister', kwargs={
            'event_pk': '3'
        }))

        self.assertEqual(response.status_code, 403)

    def test_remove_registration(self):

        attend = Attend.objects.get(event=3, user=1)
        attend.state = AttendState.waiting
        attend.save()

        response = self.client.get(reverse('eventportal_event_unregister', kwargs={
            'event_pk': '3'
        }))

        self.assertEqual(response.status_code, 200)