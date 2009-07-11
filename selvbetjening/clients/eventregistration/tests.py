from datetime import date, timedelta, datetime

from django.test import TestCase
from django.core.urlresolvers import reverse

from selvbetjening.data.events.tests import Database
from selvbetjening.data.events import models

from forms import OptionGroupForm

class EventViewTestCase(TestCase):
    def test_signoff_remove_event(self):
        user = Database.new_user(id='user')
        event = Database.new_event()

        models.Attend.objects.create(user=user, event=event)

        self.client.login(username='user', password='user')
        self.client.post(reverse('eventregistration_signoff', kwargs={'event_id' : event.id}),
                         {'confirm' : True})

        self.assertFalse(event in [ attend.event for attend in user.attend_set.all() ])
        
    def test_sigup_event(self):
        user = Database.new_user(id='user')
        event = Database.new_event()
        
        self.client.login(username='user', password='user')
        resp = self.client.get(reverse('eventregistration_signup', 
                                       kwargs={'event_id' : event.id}))
        
        self.assertTemplateUsed(resp, 'eventregistration/signup.html')
        
    def test_sigup_event_submit_form(self):
        user = Database.new_user(id='user')
        event = Database.new_event()
        
        self.client.login(username='user', password='user')
        resp = self.client.post(reverse('eventregistration_signup', 
                                       kwargs={'event_id' : event.id}),
                                {'confirm' : True})
        
        self.assertRedirects(resp, reverse('eventregistration_view', kwargs={'event_id':event.id}))
        
class EventOptionsFormTestCase(TestCase):
    def test_displayed_fields(self):
        user = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event)

        Database.new_option(optiongroup)
        Database.new_option(optiongroup)
        Database.new_option(optiongroup)

        form = OptionGroupForm(optiongroup)

        self.assertEqual(len(form.fields), 3)

    def test_displayed_fields_order(self):
        user = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event)

        Database.new_option(optiongroup, order=1, name='1')
        Database.new_option(optiongroup, order=0, name='0')
        Database.new_option(optiongroup, order=3, name='2')

        form = OptionGroupForm(optiongroup)

        id = 0
        for field in form.Meta.layout[0][1]:
            field_id = field[0]
            self.assertTrue(form.fields[field_id].label.endswith(str(id)))
            id += 1

    def test_initial_values_set(self):
        user = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event)

        option1 = Database.new_option(optiongroup)
        option2 = Database.new_option(optiongroup)

        attendee = Database.attend(user, event)
        attendee.select_option(option1)

        form = OptionGroupForm(optiongroup,
                               selected_options=attendee.selected_options)

        self.assertTrue(OptionGroupForm._get_id(option1) in form.initial)
        self.assertFalse(OptionGroupForm._get_id(option2) in form.initial)

class EventOptionsFormUsageTestCase(TestCase):
    def test_deselect(self):
        user = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event)

        option1 = Database.new_option(optiongroup)
        option2 = Database.new_option(optiongroup)

        attendee = Database.attend(user, event)
        attendee.select_option(option1)

        form = OptionGroupForm(optiongroup, {},
                               selected_options=attendee.selected_options)

        self.assertTrue(form.is_valid())
        form.save_selection(attendee)

        self.assertEqual(len(user.option_set.all()), 0)

    def test_select(self):
        user = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event)

        option1 = Database.new_option(optiongroup)
        option2 = Database.new_option(optiongroup)

        attendee = Database.attend(user, event)
        attendee.select_option(option1)

        form = OptionGroupForm(optiongroup, 
                               {OptionGroupForm._get_id(option1) : True,
                                OptionGroupForm._get_id(option2) : True},
                               selected_options=attendee.selected_options)

        self.assertTrue(form.is_valid())
        
        form.save_selection(attendee)
        
        self.assertEqual(len(attendee.selected_options), 2)

class EventOptionsFormValidationGroupValidationTestCase(TestCase):
    def test_minimum_selected_limit_not_satisfied(self):
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event, min_select=2)
        option = Database.new_option(optiongroup)

        form = OptionGroupForm(optiongroup, {OptionGroupForm._get_id(option) : True})

        self.assertFalse(form.is_valid())

    def test_select_limit_satisfied(self):
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event, min_select=1)
        option = Database.new_option(optiongroup)

        form = OptionGroupForm(optiongroup, {OptionGroupForm._get_id(option) : True})

        self.assertTrue(form.is_valid())

    def test_maximum_selected_limit_exceeded(self):
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event, max_select=1)
        option1 = Database.new_option(optiongroup)
        option2 = Database.new_option(optiongroup)

        form = OptionGroupForm(optiongroup, {OptionGroupForm._get_id(option1) : True,
                                             OptionGroupForm._get_id(option2) : True})

        self.assertFalse(form.is_valid())

    def test_maximum_limit_satisfied(self):
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event, max_select=2)
        option1 = Database.new_option(optiongroup)
        option2 = Database.new_option(optiongroup)

        form = OptionGroupForm(optiongroup, {OptionGroupForm._get_id(option1) : True,
                                             OptionGroupForm._get_id(option2) : True})

        self.assertTrue(form.is_valid())

    def test_max_attendees_exceeded(self):
        user1 = Database.new_user()
        user2 = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event, max_attend=1)
        option = Database.new_option(optiongroup)
        
        attend1 = Database.attend(user1, event)
        attend1.select_option(option)

        form = OptionGroupForm(optiongroup, 
                               {OptionGroupForm._get_id(option) : True})

        self.assertFalse(form.is_valid())

    def test_max_attendees_reselect(self):
        user = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event, max_attend=1)
        option = Database.new_option(optiongroup)
        
        attendee = Database.attend(user, event)
        attendee.select_option(option)

        form = OptionGroupForm(optiongroup, 
                               {OptionGroupForm._get_id(option) : True},
                               selected_options=attendee.selected_options)

        self.assertTrue(form.is_valid())
        form.save_selection(attendee)
        self.assertEqual(len(attendee.selected_options), 1)

    def test_select_frozen_option(self):
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event, freeze_time=datetime.today() - timedelta(days=1))
        option = Database.new_option(optiongroup)

        form = OptionGroupForm(optiongroup, {OptionGroupForm._get_id(option) : True})

        self.assertTrue(optiongroup.is_frozen())
        self.assertFalse(form.is_valid())

    def test_deselect_frozen_option(self):
        user = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event, freeze_time=datetime.today() - timedelta(days=1))
        option = Database.new_option(optiongroup)
        
        attendee = Database.attend(user, event)
        attendee.select_option(option)

        form = OptionGroupForm(optiongroup, {})

        self.assertTrue(form.is_valid())
        form.save_selection(attendee)
        self.assertEqual(len(attendee.selected_options), 1)