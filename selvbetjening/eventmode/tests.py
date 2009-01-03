from datetime import date, timedelta

from django.test import TestCase
from django.core.urlresolvers import reverse

from selvbetjening.events.models import Event

from models import EventmodeMachine
from middleware import Eventmode

class DatabaseSetup(object):
    @staticmethod
    def setUp(target):
        day = timedelta(days=1)
        today = date.today()

        target.event = Event.objects.create(title='event1', registration_open=True,
                                        enddate=today, startdate=today-day)

        target.event2 = Event.objects.create(title='event1', registration_open=True,
                                        enddate=today-day, startdate=today-day*2)

        target.eventmode1 = EventmodeMachine.objects.create(passphrase='ww',
                                                            event=target.event,
                                                            name='m1')

        target.eventmode2 = EventmodeMachine.objects.create(passphrase='www',
                                                            event=target.event2,
                                                            name='m2')

class EventmodeMachineTestCase(TestCase):
    def setUp(self):
        DatabaseSetup.setUp(self)

    def test_is_valid(self):
        self.assertTrue(self.eventmode1.is_valid())
        self.assertFalse(self.eventmode2.is_valid())

    def test_check_passphrase(self):
        self.assertTrue(EventmodeMachine.objects.authenticate(self.event, 'ww') is not None)

    def test_check_passphrase_wrong(self):
        self.assertTrue(EventmodeMachine.objects.authenticate(self.event, 'wrong_pp') is None)

    def test_check_passphrase_wrong_event(self):
        self.assertTrue(EventmodeMachine.objects.authenticate(self.event2, 'ww') is None)

class EventmodeTestCase(TestCase):
    def setUp(self):
        DatabaseSetup.setUp(self)

        class DummyRequest():
            session = {}

        self.dummy_request = DummyRequest()
        self.eventmode = Eventmode(self.dummy_request)

    def test_login(self):
        self.assertTrue(self.eventmode.login(self.event, 'ww'))

    def test_login_expired_machine(self):
        self.assertFalse(self.eventmode.login(self.event2, 'www'))

    def test_login_incorrect(self):
        self.assertFalse(self.eventmode.login(self.event, 'ww_random_part'))

    def test_is_not_authenticated(self):
        self.assertFalse(self.eventmode.is_authenticated())

    def test_is_authenticated(self):
        self.eventmode.login(self.event, 'ww')
        self.assertTrue(self.eventmode.is_authenticated())

    def test_is_authenticated_expired(self):
        self.eventmode.login(self.event2, 'www')
        self.assertFalse(self.eventmode.is_authenticated())

    def test_logout(self):
        self.test_login()
        self.assertTrue(self.eventmode.is_authenticated())

        self.eventmode.logout()
        self.assertFalse(self.eventmode.is_authenticated())

    def test_model(self):
        self.test_login()
        self.assertEqual(self.eventmode.model, self.eventmode1)

class MiddlewareTestCase(TestCase):

    def test_is_loaded(self):
        # fails authentication check if eventmode middleware is missing
        response = self.client.get(reverse('eventmode_index'))

        self.assertEqual(response.status_code, 302)
