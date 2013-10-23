from datetime import datetime, date, timedelta

from django.test import TestCase

from selvbetjening.core.user.models import SUser
from selvbetjening.core.events.models import Attend, Event, OptionGroup
from selvbetjening.core.events.options.dynamic_selections import dynamic_selections_form_factory, _pack_id, SCOPE, \
    dynamic_selections

import models


class Database(object):
    _id = 0
    @classmethod
    def new_id(cls):
        cls._id += 1
        return str(cls._id)

    @classmethod
    def new_event(cls,
                  move_to_accepted_policy=None):

        kwargs = {}

        if move_to_accepted_policy is not None:
            kwargs['move_to_accepted_policy'] = move_to_accepted_policy

        return models.Event.objects.create(title=cls.new_id(),
                                           startdate=date.today(),
                                           enddate=date.today(),
                                           registration_open=True,
                                           **kwargs)

    @classmethod
    def new_user(cls, id=None):
        if id is None:
            id = cls.new_id()
        return SUser.objects.create_user(id, '%s@example.org' % id, id)

    @classmethod
    def attend(cls, user, event):
        return models.Attend.objects.create(user=user, event=event)

    @classmethod
    def new_optiongroup(cls, event, min_select=0, max_select=0, freeze_time=None):
        if freeze_time is None:
            freeze_time = datetime.now() + timedelta(days=1)
        return models.OptionGroup.objects.create(event=event,
                                                 name=cls.new_id(),
                                                 minimum_selected=min_select,
                                                 maximum_selected=max_select,
                                                 freeze_time=freeze_time)

    @classmethod
    def new_option(cls, optiongroup, name=None, order=0, id=None):
        if name is None:
            name = cls.new_id()

        kwargs = {'group' : optiongroup, 'name' : name, 'order' : order}

        if id is not None:
            kwargs['id'] = id

        return models.Option.objects.create(**kwargs)


class AttendModelTestCase(TestCase):
    def test_is_new(self):
        user = Database.new_user()
        event = Database.new_event()

        attend = models.Attend.objects.create(user=user, event=event)

        self.assertTrue(attend.is_new)


class EventModelTestCase(TestCase):
    def test_attendee_order(self):
        event = Database.new_event()

        self.userarray = []
        for i in range(30):
            self.userarray.append(SUser.objects.create_user('user%s' % i, 'user@example.org', ''))
            models.Attend.objects.create(event=event, user=self.userarray[i])

        for i in range(30):
            self.assertEqual(event.attendees[i].user, self.userarray[i])

    def test_remove_attendee(self):
        user = Database.new_user()
        event = Database.new_event()
        attend = Database.attend(user, event)

        self.assertTrue(event.is_attendee(user))
        attend.delete()
        self.assertFalse(event.is_attendee(user))


class DynamicSelectionsTestCase(TestCase):
    fixtures = ['formbuilder_test_fixture.json']

    def test_scopes(self):

        event = Event.objects.get(pk=1)
        attendee = Attend.objects.all()[0]

        self.assertEqual(len(dynamic_selections(SCOPE.VIEW_REGISTRATION, attendee)), 4)
        self.assertEqual(len(dynamic_selections(SCOPE.EDIT_REGISTRATION, attendee)), 3)

    def test_ordering(self):

        event = Event.objects.get(pk=1)
        attendee = Attend.objects.get(pk=1)

        selections = dynamic_selections(SCOPE.VIEW_REGISTRATION, attendee)

        # correct ordering
        # option group 1
        #    option 1
        #    option 2
        # option group 2
        #    option 3
        #    option 4

        self.assertEqual(selections[0][0].group.pk, 1)
        self.assertEqual(selections[0][0].pk, 1)
        self.assertEqual(selections[1][0].pk, 2)

        self.assertEqual(selections[2][0].group.pk, 2)
        self.assertEqual(selections[2][0].pk, 3)
        self.assertEqual(selections[3][0].pk, 4)


class FormBuilderTestCase(TestCase):
    fixtures = ['formbuilder_test_fixture.json']

    def test_basic_form_building(self):

        instance = OptionGroup.objects.all()[0]

        form_class = dynamic_selections_form_factory(SCOPE.SADMIN, instance)
        form = form_class()

        self.assertEqual(len(form.fields), 2)

    def test_saving_selections_to_existing_attendee(self):

        option_group = OptionGroup.objects.all()[0]
        attendee = Attend.objects.all()[0]

        OptionGroupSelectionsForm = dynamic_selections_form_factory(SCOPE.SADMIN, option_group)
        form = OptionGroupSelectionsForm({}, attendee=attendee)

        self.assertTrue(form.is_valid())
        self.assertTrue(hasattr(form, 'cleaned_data'))

        form.save()

        for option, selected in dynamic_selections(SCOPE.VIEW_REGISTRATION, attendee, option_group=option_group):
            self.assertFalse(selected)

        post = {
            _pack_id('option', 1): "1",
            _pack_id('option', 2): "1"
        }

        form = OptionGroupSelectionsForm(post, attendee=attendee)

        self.assertTrue(form.is_valid())

        self.assertTrue(hasattr(form, 'cleaned_data'))
        self.assertTrue(form.cleaned_data[_pack_id('option', 1)])
        self.assertTrue(form.cleaned_data[_pack_id('option', 2)])

        form.save()

        for option, selected in dynamic_selections(SCOPE.VIEW_REGISTRATION,
                                                   attendee,
                                                   option_group=option_group):
            self.assertTrue(selected)

    def test_saving_selections_to_new_attendee(self):

        option_group = OptionGroup.objects.all()[0]
        attendee = Attend.objects.all()[0]

        OptionGroupSelectionsForm = dynamic_selections_form_factory(SCOPE.SADMIN, option_group)

        post = {
            _pack_id('option', 1): "1",
            _pack_id('option', 2): "1"
        }

        form = OptionGroupSelectionsForm(post)

        self.assertTrue(form.is_valid())

        self.assertTrue(hasattr(form, 'cleaned_data'))
        self.assertTrue(form.cleaned_data[_pack_id('option', 1)])
        self.assertTrue(form.cleaned_data[_pack_id('option', 2)])

        form.save(attendee=attendee)

        for option, selected in dynamic_selections(SCOPE.VIEW_REGISTRATION,
                                                   attendee,
                                                   option_group=option_group):
            self.assertTrue(selected)

    def test_delete_existing_selections(self):

        option_group = OptionGroup.objects.all()[0]
        attendee = Attend.objects.get(pk=2)

        for option, selection in dynamic_selections(SCOPE.VIEW_REGISTRATION,
                                                    attendee,
                                                    option_group=option_group):
            self.assertIsNotNone(selection)

        OptionGroupSelectionsForm = dynamic_selections_form_factory(SCOPE.SADMIN, option_group)

        form = OptionGroupSelectionsForm({})

        self.assertTrue(form.is_valid())

        self.assertTrue(hasattr(form, 'cleaned_data'))
        self.assertFalse(form.cleaned_data[_pack_id('option', 1)])
        self.assertFalse(form.cleaned_data[_pack_id('option', 2)])

        form.save(attendee=attendee)

        for option, selected in dynamic_selections(SCOPE.VIEW_REGISTRATION, attendee, option_group=option_group):
            self.assertFalse(selected)

    def test_text_option_type(self):

        option_group = OptionGroup.objects.get(pk=2)
        attendee = Attend.objects.get(pk=2)

        post = {
            _pack_id("option", 3): "some text",
        }

        OptionGroupSelectionsForm = dynamic_selections_form_factory(SCOPE.SADMIN, option_group)
        form = OptionGroupSelectionsForm(post, attendee=attendee)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data[_pack_id('option', 3)], "some text")

        form.save()

        selections = dynamic_selections(SCOPE.VIEW_REGISTRATION,
                                        attendee,
                                        option_group=option_group,
                                        as_dict=True)

        option, selection = selections[3]
        self.assertIsNotNone(selection)
        self.assertEqual(selection.text, "some text")

    def test_choice_option_type(self):

        option_group = OptionGroup.objects.get(pk=2)
        attendee = Attend.objects.get(pk=2)

        post = {
            _pack_id("option", 4): "suboption_1",
        }

        OptionGroupSelectionsForm = dynamic_selections_form_factory(SCOPE.SADMIN, option_group)
        form = OptionGroupSelectionsForm(post, attendee=attendee)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data[_pack_id('option', 4)], "suboption_1")

        form.save()

        selections = dynamic_selections(SCOPE.VIEW_REGISTRATION, attendee,
                                        option_group=option_group,
                                        as_dict=True)
        option, selection = selections[4]
        self.assertIsNotNone(selection)
        self.assertIsNotNone(selection.suboption)
        self.assertEqual(selection.suboption.pk, 1)
