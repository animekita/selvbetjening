from datetime import date, timedelta

from django.test import TestCase
from django.contrib.auth import models as auth_models
from django.core.urlresolvers import reverse

from events.forms import OptionsForm
from events import models

class DatabaseSetup(object):
    @staticmethod
    def setup(target):
        target.user1 = auth_models.User.objects.create_user('user1', 'user@example.org', 'user1')
        target.user2 = auth_models.User.objects.create_user('user2', 'user@example.org', 'user2')
        target.user3 = auth_models.User.objects.create_user('user3', 'user@example.org', 'user3')
        
        target.event1 = models.Event.objects.create(title='event', 
                                                  startdate=date.today(),
                                                  enddate=date.today(),
                                                  registration_open=True)
        
        target.event2 = models.Event.objects.create(title='event', 
                                                  startdate=date.today(),
                                                  enddate=date.today() + timedelta(days=2),
                                                  registration_open=False)   
        
        target.event3 = models.Event.objects.create(title='event', 
                                                  startdate=date.today(),
                                                  enddate=date.today() + timedelta(days=2),
                                                  registration_open=False)
        
        target.event4 = models.Event.objects.create(title='event', 
                                                  startdate=date(2008, 11, 12),
                                                  enddate=date(2008, 11, 14),
                                                  registration_open=True)    
        
        target.event2.add_attendee(target.user1)
        target.event2.add_attendee(user=target.user2, has_attended=True)
        
        target.option1 = models.Option.objects.create(event=target.event1, 
                                                    description='hello3', 
                                                    order=5)
        target.option2 = models.Option.objects.create(event=target.event1, 
                                                    description='hello1', 
                                                    order=2)
        target.option3 = models.Option.objects.create(event=target.event1, 
                                                    description='hello2', 
                                                    order=3)

        target.option11 = models.Option.objects.create(event=target.event2, 
                                                    description='hello11', 
                                                    order=5)
        target.option12 = models.Option.objects.create(event=target.event2, 
                                                    description='hello12', 
                                                    order=2)        
        
        target.option1.users.add(target.user2)
        target.option3.users.add(target.user2)
        target.option11.users.add(target.user2)
        target.option12.users.add(target.user2)
        
        target.form = {}
        target.form[1] = OptionsForm(target.user1, target.event1)
        target.form[2] = OptionsForm(target.user2, target.event1)

class EventModelTestCase(TestCase):
    
    def setUp(self):
        DatabaseSetup.setup(self)    
    
    def test_is_registration_open(self):
        self.assertTrue(self.event1.is_registration_open())
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
        
    def test_attendee_order(self):
        self.userarray = []
        for i in range(30):
            self.userarray.append(auth_models.User.objects.create_user(i, 'user1', 'user@example.org'))
            self.event3.add_attendee(self.userarray[i], has_attended=False)
            
        self.event3.add_attendee(self.user1, has_attended=False)
        
        attendees = self.event3.get_attendees()
        
        for i in range(30):
            self.assertEqual(attendees[i].user, self.userarray[i])
            
        self.assertEqual(attendees[30].user, self.user1)   
        
class EventOptionsFormTestCase(TestCase):
    def setUp(self):
        DatabaseSetup.setup(self)
        
    def test_initialization(self):
        self.assertEqual(len(self.form[1].fields), 3)
        
    def test_order(self):
        
        int = 1        
        for field_id in self.form[1].fields:
            self.assertTrue(self.form[1].fields[field_id].label.endswith(str(int)))
            int = int + 1
    
    def test_selected_initial(self):
        self.assertEqual(self.form[1].initial, {})

        self.assertTrue(OptionsForm._get_id(self.option1) in self.form[2].initial)
        self.assertTrue(OptionsForm._get_id(self.option3) in self.form[2].initial)
        self.assertFalse(OptionsForm._get_id(self.option2) in self.form[2].initial)
        
    def test_no_change(self):  
        self._save_forms()
        
        self.assertEqual(len(self.user1.option_set.all()), 0)
        self.assertEqual(len(self.user2.option_set.all()), 4)
        
    def test_select(self):
        self.form[3] = OptionsForm(self.user1, self.event1, 
                                 {OptionsForm._get_id(self.option1) : True,
                                  OptionsForm._get_id(self.option2) : True})
        
        self.form[4] = OptionsForm(self.user2, self.event1, 
                                 {OptionsForm._get_id(self.option1) : True, 
                                  OptionsForm._get_id(self.option3) : True})
        
        self._save_forms()
        
        self.assertEqual(len(self.user1.option_set.all()), 2)
        self.assertEqual(len(self.user2.option_set.all()), 4)
    
    def test_deselect(self):
        self.form[3] = OptionsForm(self.user2, self.event1, 
                                 {OptionsForm._get_id(self.option1) : True})
        
        self._save_forms()
        
        self.assertEqual(len(self.user2.option_set.all()), 3)
        
    def _save_forms(self):
        for form_id in self.form:
            self.form[form_id].is_valid()
            self.form[form_id].save()

class EventViewTestCase(TestCase):
    def setUp(self):
        DatabaseSetup.setup(self)
        self.event2.registration_open = True
        self.event2.save()

    def test_signoff_remove_event(self):
        self.assertFalse(self.event2 not in [ attend.event for attend in self.user2.attend_set.all() ])       
        self._signoff()
        self.assertTrue(self.event2 not in [ attend.event for attend in self.user2.attend_set.all() ])       
        
    def test_signoff_remove_options(self):
        self.assertEqual(len(self.user2.option_set.all()), 4)
        self._signoff()
        self.assertEqual(len(self.user2.option_set.all()), 2)
    
    def _signoff(self):
        self.client.login(username='user2', password='user2')
        self.client.post(reverse('events_signoff', kwargs={'event_id':self.event2.id}), 
                         {'confirm' : True})