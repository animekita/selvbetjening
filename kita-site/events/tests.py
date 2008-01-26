from datetime import date, timedelta

from django.test import TestCase
from django.contrib.auth import models as auth_models

from events import models

class EventModelTestCase(TestCase):
    
    def setUp(self):
        self.user1 = auth_models.User.objects.create_user('user1', 'user1', 'user@example.org')
        self.user2 = auth_models.User.objects.create_user('user2', 'user1', 'user@example.org')
        self.user3 = auth_models.User.objects.create_user('user3', 'user1', 'user@example.org')
        
        self.event1 = models.Event.objects.create(title='event', 
                                                  startdate=date.today(),
                                                  enddate=date.today() + timedelta(days=2),
                                                  registration_open=True)
        
        self.event2 = models.Event.objects.create(title='event', 
                                                  startdate=date.today(),
                                                  enddate=date.today() + timedelta(days=2),
                                                  registration_open=False)

        self.event2.add_attendee(self.user1)
        self.event2.add_attendee(user=self.user2, has_attended=True)
        
        self.event3 = models.Event.objects.create(title='event', 
                                                  startdate=date.today(),
                                                  enddate=date.today() + timedelta(days=2),
                                                  registration_open=False)
        
        self.event4 = models.Event.objects.create(title='event', 
                                                  startdate=date(2008, 11, 12),
                                                  enddate=date(2008, 11, 14),
                                                  registration_open=True)    
    
    def test_is_registration_open(self):
        self.assertTrue(self.event1.is_registration_open())
        self.assertFalse(self.event2.is_registration_open())
        self.assertFalse(self.event2.is_registration_open())
        
    def test_no_guests(self):
        self.assertTrue(len(self.event1.get_attendees()) == 0)
        
    def test_guests(self):
        self.assertEqual(len(self.event2.get_attendees()), 2)
        
    def test_is_signedup(self):
        self.assertTrue(self.event2.is_attendee(self.user1))
    
    def test_is_signedup_not(self):
        self.assertFalse(self.event2.is_attendee(self.user3))
    
    def test_delete_guest(self):
        self.event3.add_attendee(self.user1, has_attended=False)
        self.assertEqual(len(self.event3.get_attendees()), 1)
        
        self.event3.remove_attendee(self.user1)
        self.assertEqual(len(self.event3.get_attendees()), 0)