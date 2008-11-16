from datetime import date, timedelta

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from eventmode.models import Eventmode as EventmodeModel
from eventmode.middleware import Eventmode

from events.models import Event

class DatabaseSetup(object):
    def setUp(target):
        day = timedelta(days=1)
        today = date.today()

        target.event = Event.objects.create(title='event1', registration_open=True,
                                        enddate=today, startdate=today-day)

        target.event2 = Event.objects.create(title='event1', registration_open=True,
                                        enddate=today-day, startdate=today-day*2)

        target.eventmode1 = EventmodeModel.objects.create(passphrase='ww',
                                                        event=target.event)

        target.eventmode2 = EventmodeModel.objects.create(passphrase='www',
                                                        event=target.event2)
    setUp = staticmethod(setUp)

class EventmodeModelTestCase(TestCase):
    def setUp(self):
        DatabaseSetup.setUp(self)

    def test_is_valid(self):
        self.assertTrue(self.eventmode1.is_valid())
        self.assertFalse(self.eventmode2.is_valid())

    def test_check_passphrase(self):
        self.assertTrue(EventmodeModel.objects.check_passphrase('ww'))

    def test_check_passphrase_wrong(self):
        self.assertFalse(EventmodeModel.objects.check_passphrase('ww_random_part'))

class EventmodeTestCase(TestCase):
    def setUp(self):
        DatabaseSetup.setUp(self)

        class dummyRequest():
            session = {}

        self.dummyRequest = dummyRequest()
        self.eventmode = Eventmode(self.dummyRequest)

    def test_activate(self):
        self.assertTrue(self.eventmode.activate('ww'))

    def test_activate_old(self):
        self.assertFalse(self.eventmode.activate('www'))

    def test_activate_nonexisting(self):
        self.assertFalse(self.eventmode.activate('ww_random_part'))

    def test_is_not_active(self):
        self.assertFalse(self.eventmode.is_active())

    def test_is_active(self):
        self.eventmode.activate('ww')
        self.assertTrue(self.eventmode.is_active())

    def test_is_active_old(self):
        self.eventmode.activate('www')
        self.assertFalse(self.eventmode.is_active())

    def test_deactivate(self):
        self.test_is_active()
        self.assertTrue(self.eventmode.is_active())

        self.eventmode.deactivate()
        self.assertFalse(self.eventmode.is_active())

    def test_get_model(self):
        self.test_is_active()
        self.assertEqual(self.eventmode.get_model(), self.eventmode1)
