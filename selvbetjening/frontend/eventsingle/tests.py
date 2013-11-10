from django.core.urlresolvers import reverse
from django.test import TestCase
from selvbetjening.core.events.models import Attend, AttendState


class SingleEventTestCase(TestCase):

    fixtures = ['sdemo-example-site.json']

    def setUp(self):
        self.client.login(username='admin', password='admin')

    def test_step2(self):

        s = self.client.session
        s['user-data-verified'] = True
        s.save()

        # Try to load the page

        response = self.client.get(reverse('eventsingle_step2', kwargs={'event_pk': 3}))
        self.assertEqual(response.status_code, 200)

        # Post, try to attend
        response = self.client.post(reverse('eventsingle_step2', kwargs={'event_pk': 3}), {})
        self.assertEqual(response.status_code, 302)

        # We should now be attending the event
        attend = Attend.objects.get(user__username='admin', event__pk=3)
        self.assertEqual(attend.state, AttendState.accepted)