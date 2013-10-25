
from django.core.urlresolvers import reverse
from django.test import TestCase

from selvbetjening.core.events.models import Event, Attend, AttendState, AttendeeComment, OptionGroup


class EventTestCase(TestCase):

    fixtures = ['sdemo-example-site.json']

    def setUp(self):
        self.client.login(username='admin', password='admin')

    def test_event_overview(self):

        url = reverse('sadmin2:event_overview', kwargs={'event_pk': 1})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_event_attendees(self):

        url = reverse('sadmin2:event_attendees', kwargs={'event_pk': 1})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_event_attendees_add(self):

        url = reverse('sadmin2:event_attendees_add', kwargs={'event_pk': 1})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Attend.objects.filter(event__pk=1).count(), 1)

        response = self.client.post(url, {
            'user_pk': 1
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Attend.objects.filter(event__pk=1).count(), 2)

    def test_event_attendee(self):

        url = reverse('sadmin2:event_attendee', kwargs={
            'event_pk': 1,
            'attendee_pk': 1
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Status button (waiting)

        response = self.client.post(url, {
            'action': 'to-state-waiting'
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        # TODO disable to "waiting" status button if the event policy prevents this status
        attendee = Attend.objects.get(pk=1)
        self.assertEqual(attendee.state, AttendState.accepted)

        # Status button (accepted)

        response = self.client.post(url, {
            'action': 'to-state-accepted'
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        attendee = Attend.objects.get(pk=1)
        self.assertEqual(attendee.state, AttendState.accepted)

        # Status button (attended)

        response = self.client.post(url, {
            'action': 'to-state-attended'
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        attendee = Attend.objects.get(pk=1)
        self.assertEqual(attendee.state, AttendState.attended)

        # Pay

        response = self.client.post(url, {
            'action': 'pay',
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        attendee = Attend.objects.get(pk=1)
        self.assertEqual(attendee.paid, 0)

    def test_event_attendee_unpaid(self):

        url = reverse('sadmin2:event_attendee', kwargs={
            'event_pk': 2,
            'attendee_pk': 2
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Pay

        response = self.client.post(url, {
            'action': 'pay',
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        attendee = Attend.objects.get(pk=2)
        self.assertEqual(attendee.paid, 300)

    def test_event_attendee_payments(self):

        url = reverse('sadmin2:event_attendee_payments', kwargs={
            'event_pk': 2,
            'attendee_pk': 2
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {
            'amount': 200
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        attendee = Attend.objects.get(pk=2)
        self.assertEqual(attendee.paid, 200)
        self.assertEqual(attendee.unpaid, 100)

    def test_event_attendee_selections(self):

        url = reverse('sadmin2:event_attendee_selections', kwargs={
            'event_pk': 2,
            'attendee_pk': 2
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {

        }, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_event_attendee_notes(self):

        url = reverse('sadmin2:event_attendee_notes', kwargs={
            'event_pk': 2,
            'attendee_pk': 2
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {
            'comment': 'A user note'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(AttendeeComment.objects.filter(attendee__pk=2).count(), 1)

    def test_event_selections(self):

        url = reverse('sadmin2:event_selections', kwargs={
            'event_pk': 2
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_event_selections_transfer(self):

        # TODO add much more detailed tests for selection transfer

        url = reverse('sadmin2:event_selections_transfer', kwargs={
            'event_pk': 2
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_event_selections_manage(self):

        # TODO test create anon group
        # TODO detailed testing of changing scopes

        url = reverse('sadmin2:event_selections_manage', kwargs={
            'event_pk': 2
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {

        }, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_event_selections_create_group(self):
        url = reverse('sadmin2:event_selections_create_group', kwargs={
            'event_pk': 2
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {
            'name': 'NewGroup',
            'minimum_selected': 0,
            'maximum_selected': 0,
            'package_price': 0
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(OptionGroup.objects.filter(name='NewGroup').exists())

    def test_event_selections_edit_group(self):
        url = reverse('sadmin2:event_selections_edit_group', kwargs={
            'event_pk': 2,
            'group_pk': 2
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {
            'name': 'NewGroupName',
            'minimum_selected': 0,
            'maximum_selected': 0,
            'package_price': 0
        }, follow=True)

        self.assertEqual(response.status_code, 200)

        option_group = OptionGroup.objects.get(pk=2)
        self.assertEqual(option_group.name, 'NewGroupName')

    def test_event_account(self):

        url = reverse('sadmin2:event_account', kwargs={
            'event_pk': 2
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_event_settings(self):

        url = reverse('sadmin2:event_settings', kwargs={
            'event_pk': 2
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {
            'title': 'NewEventName',
            'move_to_accepted_policy': 'always',
            'maximum_attendees': 0
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(Event.objects.filter(title='NewEventName').exists())

    def test_event_report_check_in(self):

        url = reverse('sadmin2:event_report_check_in', kwargs={
            'event_pk': 2
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_event_report_registration(self):

        url = reverse('sadmin2:event_report_registration', kwargs={
            'event_pk': 2
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)