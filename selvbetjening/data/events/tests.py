from datetime import date, timedelta, datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from forms import OptionGroupForm
import models

class Database(object):
    _id = 0
    @classmethod
    def new_id(cls):
        cls._id += 1
        return str(cls._id)

    @classmethod
    def new_event(cls):
        return models.Event.objects.create(title=cls.new_id(),
                                           startdate=date.today(),
                                           enddate=date.today(),
                                           registration_open=True)

    @classmethod
    def new_user(cls, id=None):
        if id is None:
            id = cls.new_id()
        return User.objects.create_user(id, '%s@example.org' % id, id)

    @classmethod
    def new_optiongroup(cls, event, min_select=0, max_select=0, max_attend=0, freeze_time=None):
        if freeze_time is None:
            freeze_time = date.today() + timedelta(days=1)
        return models.OptionGroup.objects.create(event=event,
                                                 name=cls.new_id(),
                                                 minimum_selected=min_select,
                                                 maximum_selected=max_select,
                                                 maximum_attendees=max_attend,
                                                 freeze_time=freeze_time)

    @classmethod
    def new_option(cls, optiongroup, name=None, order=0):
        if name is None:
            name = cls.new_id()

        return models.Option.objects.create(group=optiongroup,
                                            name=name,
                                            order=order)

class AttendModelTestCase(TestCase):
    def test_is_new(self):
        user = Database.new_user()
        event = Database.new_event()

        attend = models.Attend(user=user, event=event)

        self.assertTrue(attend.is_new)

class EventModelTestCase(TestCase):
    def test_attendee_order(self):
        user = Database.new_user()
        event = Database.new_event()

        self.userarray = []
        for i in range(30):
            self.userarray.append(User.objects.create_user('user%s' % i, 'user@example.org', ''))
            event.add_attendee(self.userarray[i], has_attended=False)

        event.add_attendee(user, has_attended=False)

        for i in range(30):
            self.assertEqual(event.attendees[i].user, self.userarray[i])

        self.assertEqual(event.attendees[30].user, user)

class EventOptionsFormTestCase(TestCase):
    def test_displayed_fields(self):
        user = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event)

        Database.new_option(optiongroup)
        Database.new_option(optiongroup)
        Database.new_option(optiongroup)

        form = OptionGroupForm(user, optiongroup)

        self.assertEqual(len(form.fields), 3)

    def test_displayed_fields_order(self):
        user = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event)

        Database.new_option(optiongroup, order=1, name='1')
        Database.new_option(optiongroup, order=0, name='0')
        Database.new_option(optiongroup, order=3, name='2')

        form = OptionGroupForm(user, optiongroup)

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

        option1.users.add(user)

        form = OptionGroupForm(user, optiongroup)

        self.assertTrue(OptionGroupForm._get_id(option1) in form.initial)
        self.assertFalse(OptionGroupForm._get_id(option2) in form.initial)

class EventOptionsFormUsageTestCase(TestCase):
    def test_deselect(self):
        user = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event)

        option1 = Database.new_option(optiongroup)
        option2 = Database.new_option(optiongroup)

        option1.users.add(user)

        form = OptionGroupForm(user, optiongroup, {})

        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(len(user.option_set.all()), 0)

    def test_select(self):
        user = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event)

        option1 = Database.new_option(optiongroup)
        option2 = Database.new_option(optiongroup)

        option1.users.add(user)

        form = OptionGroupForm(user, optiongroup, {OptionGroupForm._get_id(option1) : True,
                                                   OptionGroupForm._get_id(option2) : True})

        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(len(user.option_set.all()), 2)

class EventOptionsFormValidationGroupValidationTestCase(TestCase):
    def test_minimum_selected_limit_not_satisfied(self):
        user = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event, min_select=2)
        option = Database.new_option(optiongroup)

        form = OptionGroupForm(user, optiongroup, {OptionGroupForm._get_id(option) : True})

        self.assertFalse(form.is_valid())

    def test_select_limit_satisfied(self):
        user = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event, min_select=1)
        option = Database.new_option(optiongroup)

        form = OptionGroupForm(user, optiongroup, {OptionGroupForm._get_id(option) : True})

        self.assertTrue(form.is_valid())

    def test_maximum_selected_limit_exceeded(self):
        user = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event, max_select=1)
        option1 = Database.new_option(optiongroup)
        option2 = Database.new_option(optiongroup)

        form = OptionGroupForm(user, optiongroup, {OptionGroupForm._get_id(option1) : True,
                                                   OptionGroupForm._get_id(option2) : True})

        self.assertFalse(form.is_valid())

    def test_maximum_limit_satisfied(self):
        user = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event, max_select=2)
        option1 = Database.new_option(optiongroup)
        option2 = Database.new_option(optiongroup)

        form = OptionGroupForm(user, optiongroup, {OptionGroupForm._get_id(option1) : True,
                                                   OptionGroupForm._get_id(option2) : True})

        self.assertTrue(form.is_valid())

    def test_max_attendees_exceeded(self):
        user1 = Database.new_user()
        user2 = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event, max_attend=1)
        option = Database.new_option(optiongroup)
        option.users.add(user1)

        form = OptionGroupForm(user2, optiongroup, {OptionGroupForm._get_id(option) : True})

        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(user2 not in option.users.all())

    def test_max_attendees_reselect(self):
        user = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event, max_attend=1)
        option = Database.new_option(optiongroup)
        option.users.add(user)

        form = OptionGroupForm(user, optiongroup, {OptionGroupForm._get_id(option) : True})

        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(user in option.users.all())

    def test_select_frozen_option(self):
        user = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event, freeze_time=datetime.today() - timedelta(days=1))
        option = Database.new_option(optiongroup)

        form = OptionGroupForm(user, optiongroup, {OptionGroupForm._get_id(option) : True})

        self.assertTrue(optiongroup.is_frozen())
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(len(user.option_set.all()), 0)

    def test_deselect_frozen_option(self):
        user = Database.new_user()
        event = Database.new_event()
        optiongroup = Database.new_optiongroup(event, freeze_time=datetime.today() - timedelta(days=1))
        option = Database.new_option(optiongroup)
        option.users.add(user)

        form = OptionGroupForm(user, optiongroup, {})

        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(len(user.option_set.all()), 1)

class EventViewTestCase(TestCase):
    def test_signoff_remove_event(self):
        user = Database.new_user(id='user')
        event = Database.new_event()

        models.Attend.objects.create(user=user, event=event)

        self.client.login(username='user', password='user')
        self.client.post(reverse('events_signoff', kwargs={'event_id' : event.id}),
                         {'confirm' : True})

        self.assertFalse(event in [ attend.event for attend in user.attend_set.all() ])
