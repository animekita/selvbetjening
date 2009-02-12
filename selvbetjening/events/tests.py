from datetime import date, timedelta, datetime

from django.test import TestCase
from django.contrib.auth import models as auth_models
from django.core.urlresolvers import reverse

from forms import OptionsForm
import models

class DatabaseSetup(object):
    @staticmethod
    def setup(target):
        target.user1 = auth_models.User.objects.create_user('user1', 'user@example.org', 'user1')
        target.user2 = auth_models.User.objects.create_user('user2', 'user@example.org', 'user2')
        target.user3 = auth_models.User.objects.create_user('user3', 'user@example.org', 'user3')
        target.user4 = auth_models.User.objects.create_user('user4', 'user@example.org', 'user4')

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

        target.event5 = models.Event.objects.create(title='event w. freeze',
                                                  startdate=date.today(),
                                                  enddate=date.today(),
                                                  registration_open=True)


        target.event5.add_attendee(target.user4)

        target.event2.add_attendee(target.user1)
        target.event2.add_attendee(user=target.user2, has_attended=True)

        target.optiongroup1 = models.OptionGroup.objects.create(event=target.event1,
                                                                name='option group 1',
                                                                minimum_selected=0,
                                                                maximum_attendees=0)

        target.optiongroup2 = models.OptionGroup.objects.create(event=target.event2,
                                                                name='option group 2',
                                                                minimum_selected=1,
                                                                maximum_attendees=0)

        target.optiongroup3 = models.OptionGroup.objects.create(event=target.event5,
                                                                name='option group 3',
                                                                minimum_selected=0,
                                                                maximum_attendees=0)

        target.option1 = models.Option.objects.create(group=target.optiongroup1,
                                                    name='hello3',
                                                    order=5)
        target.option2 = models.Option.objects.create(group=target.optiongroup1,
                                                    name='hello1',
                                                    order=2)
        target.option3 = models.Option.objects.create(group=target.optiongroup1,
                                                    name='hello2',
                                                    order=3)

        target.option11 = models.Option.objects.create(group=target.optiongroup2,
                                                    name='hello11',
                                                    order=5)
        target.option12 = models.Option.objects.create(group=target.optiongroup2,
                                                    name='hello12',
                                                    order=2)

        target.option21 = models.Option.objects.create(group=target.optiongroup3,
                                                    name='hello21',
                                                    order=5,
                                                    freeze_time=datetime.now() - timedelta(days=1))
        target.option22 = models.Option.objects.create(group=target.optiongroup3,
                                                    name='hello22',
                                                    order=2)

        target.option1.users.add(target.user2)
        target.option3.users.add(target.user2)
        target.option11.users.add(target.user2)
        target.option12.users.add(target.user2)
        target.option21.users.add(target.user4)
        target.option22.users.add(target.user4)

        target.form = {}
        target.form[1] = OptionsForm(target.user1, target.event1)
        target.form[2] = OptionsForm(target.user2, target.event1)

class AttendModelTestCase(TestCase):
    def setUp(self):
        DatabaseSetup.setup(self)

    def test_is_new(self):
        attend1 = self.user1.attend_set.get(event=self.event2)
        attend2 = self.user2.attend_set.get(event=self.event2)

        self.assertTrue(attend1.is_new)
        self.assertTrue(attend2.is_new)

class EventModelTestCase(TestCase):

    def setUp(self):
        DatabaseSetup.setup(self)

    def test_is_registration_open(self):
        self.assertTrue(self.event1.is_registration_open())
        self.assertFalse(self.event2.is_registration_open())

    def test_no_guests(self):
        self.assertTrue(len(self.event1.attendees) == 0)

    def test_guests(self):
        self.assertEqual(len(self.event2.attendees), 2)

    def test_is_signedup(self):
        self.assertTrue(self.event2.is_attendee(self.user1))

    def test_is_signedup_not(self):
        self.assertFalse(self.event2.is_attendee(self.user3))

    def test_delete_guest(self):
        self.event3.add_attendee(self.user1, has_attended=False)
        self.assertEqual(len(self.event3.attendees), 1)

        self.event3.remove_attendee(self.user1)
        self.assertEqual(len(self.event3.attendees), 0)

    def test_attendee_order(self):
        self.userarray = []
        for i in range(30):
            self.userarray.append(auth_models.User.objects.create_user(i, 'user1', 'user@example.org'))
            self.event3.add_attendee(self.userarray[i], has_attended=False)

        self.event3.add_attendee(self.user1, has_attended=False)

        attendees = self.event3.attendees

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
        for field in self.form[1].Meta.layout[0][1]:
            field_id = field[0]
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
        self.assertEqual(len(self.user2.option_set.all()), 4)

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

    def test_select_limit_not_satisfied(self):
        form = OptionsForm(self.user1, self.event2, {})

        self.assertFalse(form.is_valid())

    def test_select_limit_satisfied(self):
        form = OptionsForm(self.user1, self.event2,
                           {OptionsForm._get_id(self.option11) : True,
                            OptionsForm._get_id(self.option12) : True})

        self.assertTrue(form.is_valid())

    def test_select_reselect_freeze(self):
        self.assertEqual(len(self.user4.option_set.all()), 2)

        self.form[3] = OptionsForm(self.user4, self.event5,
                                 {OptionsForm._get_id(self.option21) : True,
                                  OptionsForm._get_id(self.option22) : True})

        self._save_forms()

        self.assertEqual(len(self.user4.option_set.all()), 2)

    def test_deselect_freeze(self):
        self.assertEqual(len(self.user4.option_set.all()), 2)

        self.form[3] = OptionsForm(self.user4, self.event5,
                                  {OptionsForm._get_id(self.option22) : True})

        self._save_forms()

        self.assertEqual(len(self.user4.option_set.all()), 2)

    def test_freeze_and_limit_only_freeze(self):
        self.optiongroup3.minimum_selected = 1
        self.optiongroup3.save()

        form = OptionsForm(self.user4, self.event5,
                           {})

        self.assertTrue(form.is_valid())

    def test_freeze_and_limit_mized(self):
        self.optiongroup3.minimum_selected = 2
        self.optiongroup3.save()

        form = OptionsForm(self.user4, self.event5,
                           {OptionsForm._get_id(self.option22) : True})

        self.assertTrue(form.is_valid())

    def test_freeze_and_limit_not_satisfied(self):
        self.optiongroup3.minimum_selected = 2
        self.optiongroup3.save()

        form = OptionsForm(self.user4, self.event5,
                           {})

        self.assertFalse(form.is_valid())

    def test_max_attendees_reached(self):
        self.option31 = models.Option.objects.create(group=self.optiongroup3,
                                                    name='hello31',
                                                    order=2,
                                                    maximum_attendees=2)

        self.option31.users.add(self.user1)
        self.option31.users.add(self.user2)

        form = OptionsForm(self.user4, self.event5, {OptionsForm._get_id(self.option31) : True,})

        self.assertFalse(form.is_valid())

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
        self.assertTrue(self.event2 in [ attend.event for attend in self.user2.attend_set.all() ])
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
