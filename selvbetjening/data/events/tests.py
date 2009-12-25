from datetime import date, timedelta, datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

import models

class Database(object):
    _id = 0
    @classmethod
    def new_id(cls):
        cls._id += 1
        return str(cls._id)

    @classmethod
    def new_event(cls, maximum_attendees=0,
                  move_to_accepted_policy=None):

        kwargs = {}

        if move_to_accepted_policy is not None:
            kwargs['move_to_accepted_policy'] = move_to_accepted_policy

        return models.Event.objects.create(title=cls.new_id(),
                                           startdate=date.today(),
                                           enddate=date.today(),
                                           registration_open=True,
                                           maximum_attendees=maximum_attendees,
                                           **kwargs)

    @classmethod
    def new_user(cls, id=None):
        if id is None:
            id = cls.new_id()
        return User.objects.create_user(id, '%s@example.org' % id, id)

    @classmethod
    def attend(cls, user, event):
        return models.Attend.objects.create(user=user, event=event)

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
    def new_option(cls, optiongroup, name=None, order=0, id=None, maximum_attendees=0):
        if name is None:
            name = cls.new_id()

        kwargs = {'group' : optiongroup, 'name' : name, 'order' : order}

        if id is not None:
            kwargs['id'] = id

        return models.Option.objects.create(maximum_attendees=maximum_attendees, **kwargs)

class AttendModelTestCase(TestCase):
    def test_is_new(self):
        user = Database.new_user()
        event = Database.new_event()

        attend = models.Attend(user=user, event=event)

        self.assertTrue(attend.is_new)

class EventModelTestCase(TestCase):
    def test_attendee_order(self):
        event = Database.new_event()

        self.userarray = []
        for i in range(30):
            self.userarray.append(User.objects.create_user('user%s' % i, 'user@example.org', ''))
            event.add_attendee(self.userarray[i])

        for i in range(30):
            self.assertEqual(event.attendees[i].user, self.userarray[i])

    def test_remove_attendee(self):
        user = Database.new_user()
        event = Database.new_event()
        attend = Database.attend(user, event)

        self.assertTrue(event.is_attendee(user))
        event.remove_attendee(user)
        self.assertFalse(event.is_attendee(user))
