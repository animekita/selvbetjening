from datetime import timedelta, datetime

from django.test import TestCase
from django.core.urlresolvers import reverse

from selvbetjening.core.events.tests import Database
from selvbetjening.core.events import models

from forms import OptionGroupForm

class EventViewTestCase(TestCase):
    def test_signoff_remove_event(self):
        user = Database.new_user(id='user')
        event = Database.new_event()
        Database.attend(user, event)

        self.client.login(username='user', password='user')

        self.client.post(reverse('eventregistration_signoff', kwargs={'event_id' : event.id}),
                         {'confirm' : True})

        self.assertFalse(event in [ attend.event for attend in user.attend_set.all() ])

    def test_sigup_event(self):
        Database.new_user(id='user')
        event = Database.new_event()

        self.client.login(username='user', password='user')

        resp = self.client.get(reverse('eventregistration_signup',
                                       kwargs={'event_id' : event.id}))

        self.assertTemplateUsed(resp, 'eventregistration/signup.html')

    def test_sigup_event_submit_form(self):
        Database.new_user(id='user')
        event = Database.new_event()

        data = {'confirm' : True}

        self.client.login(username='user', password='user')

        resp = self.client.post(reverse('eventregistration_signup',
                                        kwargs={'event_id' : event.id}), data)

        self.assertRedirects(resp, reverse('eventregistration_status',
                                           kwargs={'event_id': event.id}) + '?signup=1')

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

    def test_disable_fields(self):
        event = Database.new_event(move_to_accepted_policy=models.AttendeeAcceptPolicy.always)
        optiongroup = Database.new_optiongroup(event, max_attend=1)
        option = Database.new_option(optiongroup)

        attendee1 = Database.attend(Database.new_user(), event)
        attendee1.select_option(option)

        attendee2 = Database.attend(Database.new_user(), event)

        self.assertEqual(attendee1.state, models.AttendState.accepted)
        self.assertTrue(optiongroup.max_attendees_reached())

        class TestForm(OptionGroupForm):
            option_disabled = False

            def _display_option(self, option, disabled, suboptions, **kwargs):
                if disabled:
                    self.option_disabled = True

                return super(TestForm, self)._display_option(option, disabled, suboptions, **kwargs)

        form = TestForm(optiongroup,
                        {TestForm._get_id(option) : True},
                        attendee=attendee2)

        self.assertFalse(form.is_valid())
        self.assertTrue(form.option_disabled)

    def test_initial_values_set(self):
        user = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event)

        option1 = Database.new_option(optiongroup)
        option2 = Database.new_option(optiongroup)

        attendee = Database.attend(user, event)
        attendee.select_option(option1)

        form = OptionGroupForm(optiongroup,
                               attendee=attendee)

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
                               attendee=attendee)

        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(len(attendee.selections), 0)

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
                                attendee=attendee)

        self.assertTrue(form.is_valid())

        form.save()

        self.assertEqual(len(attendee.selections), 2)

class EventOptionsFormValidationOnlyLimitAccepted(TestCase):
    def test_event_limit_reached(self):
        event = Database.new_event(maximum_attendees=1,
                                   move_to_accepted_policy=models.AttendeeAcceptPolicy.manual)

        attend1 = Database.attend(Database.new_user(), event)
        attend2 = Database.attend(Database.new_user(), event)

        self.assertEqual(0, event.accepted_attendees.count())
        self.assertFalse(event.max_attendees_reached())

        attend1.state = models.AttendState.accepted
        attend1.save()

        self.assertTrue(event.max_attendees_reached())

        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event, min_select=1)
        option = Database.new_option(optiongroup)

        form = OptionGroupForm(optiongroup,
                               {OptionGroupForm._get_id(option) : True})

        self.assertTrue(form.is_valid())

    def test_event_limit_reached_option(self):
        event = Database.new_event(move_to_accepted_policy=models.AttendeeAcceptPolicy.manual)
        optiongroup = Database.new_optiongroup(event)
        option = Database.new_option(optiongroup, maximum_attendees=1)

        attendee1 = Database.attend(Database.new_user(), event)
        attendee1.select_option(option)

        attendee2 = Database.attend(Database.new_user(), event)

        form = OptionGroupForm(optiongroup,
                               {OptionGroupForm._get_id(option) : True},
                               attendee=attendee2)

        self.assertTrue(form.is_valid())

        attendee1.state = models.AttendState.accepted
        attendee1.save()

        form = OptionGroupForm(optiongroup,
                               {OptionGroupForm._get_id(option) : True},
                               attendee=attendee2)

        self.assertFalse(form.is_valid())

    def test_event_limit_reached_group(self):
        event = Database.new_event(move_to_accepted_policy=models.AttendeeAcceptPolicy.manual)
        optiongroup = Database.new_optiongroup(event, max_attend=1)
        option = Database.new_option(optiongroup)

        attendee1 = Database.attend(Database.new_user(), event)
        attendee1.select_option(option)

        attendee2 = Database.attend(Database.new_user(), event)

        form = OptionGroupForm(optiongroup,
                               {OptionGroupForm._get_id(option) : True},
                               attendee=attendee2)

        self.assertTrue(form.is_valid())

        attendee1.state = models.AttendState.accepted
        attendee1.save()

        form = OptionGroupForm(optiongroup,
                               {OptionGroupForm._get_id(option) : True},
                               attendee=attendee2)

        self.assertFalse(form.is_valid())

class EventOptionsFormValidationGroupValidationTestCase(TestCase):
    def test_minimum_selected_limit_not_satisfied(self):
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event, min_select=2)
        option = Database.new_option(optiongroup)

        form = OptionGroupForm(optiongroup,
                               {OptionGroupForm._get_id(option) : True})

        self.assertFalse(form.is_valid())

    def test_select_limit_satisfied(self):
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event, min_select=1)
        option = Database.new_option(optiongroup)

        form = OptionGroupForm(optiongroup,
                               {OptionGroupForm._get_id(option) : True})

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
                               attendee=attendee)

        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(len(attendee.selections), 1)

    def test_select_frozen_option(self):
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event,
                                               freeze_time=datetime.today() -
                                               timedelta(days=1))
        option = Database.new_option(optiongroup)

        form = OptionGroupForm(optiongroup,
                               {OptionGroupForm._get_id(option) : True})

        self.assertTrue(optiongroup.is_frozen())
        self.assertFalse(form.is_valid())

    def test_deselect_frozen_option(self):
        user = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event, freeze_time=datetime.today() - timedelta(days=1))
        option = Database.new_option(optiongroup)

        attendee = Database.attend(user, event)
        attendee.select_option(option)

        form = OptionGroupForm(optiongroup, {}, attendee=attendee)

        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(len(attendee.selections), 1)

    def test_reselect_frozen_option(self):
        user = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event, freeze_time=datetime.today() - timedelta(days=1))
        option = Database.new_option(optiongroup)

        attendee = Database.attend(user, event)
        attendee.select_option(option)

        form = OptionGroupForm(optiongroup,
                               {OptionGroupForm._get_id(option) : True},
                               attendee=attendee)

        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(len(attendee.selections), 1)