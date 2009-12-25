from datetime import date

from django.test import TestCase
from django.contrib.auth import models as auth_models
from django.core import mail

from selvbetjening.data.members.models import UserProfile
from selvbetjening.data.events.models import Event, Attend, AttendState

from forms import SelectGroupForm
from models import Mail

class RecipientGroupFormTest(TestCase):

    def _init_users(self):
        self.users = []
        for i in range(10):
            user = auth_models.User.objects.create_user('user' + str(i), 'user' + str(i) + '@ex.ex', '')
            self.users.append(user)
            UserProfile.objects.create(user=user, dateofbirth=date.today(), send_me_email=True)

    def _init_users_advanced(self):
        for i in range(10, 20):
            user = auth_models.User.objects.create_user('user' + str(i), 'user' + str(i) + '@ex.ex', '')
            self.users.append(user)
            UserProfile.objects.create(user=user, dateofbirth=date.today(), send_me_email=False)


    def _init_events(self):
        self.events = []
        for i in range(10):
            self.events.append(Event.objects.create(title='event' + str(i), registration_open=True))

    def _init_events_attendees(self):
        self.attendees = []
        for i in range(5):
            for j in range(5):
                Attend.objects.create(user=self.users[j], event=self.events[i], state=AttendState.waiting)

    def test_select_list(self):
        form = SelectGroupForm()

        # should only contain the "all" option
        self.assertEqual(len(form.fields['group'].widget.choices), 1)

    def test_get_recipients_empty(self):
        form = SelectGroupForm({'group' : 'all'})

        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.get_selected_recipients()), 0)

    def test_get_recipients(self):
        self._init_users()

        form = SelectGroupForm({'group' : 'all'})
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.get_selected_recipients()), 10)

    def test_get_recipients_advanced(self):
        self._init_users()
        self._init_users_advanced()

        self.assertEqual(len(self.users), 20)

        form = SelectGroupForm({'group' : 'all'})
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.get_selected_recipients()), 10)

    def test_get_recipients_invalid_selection(self):
        self._init_users()

        form = SelectGroupForm({'group' : 'invalid_selection'})
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.get_selected_recipients()), 0)

    def test_select_list_events(self):
        self._init_events()
        form = SelectGroupForm()

        self.assertEqual(len(form.fields['group'].widget.choices), 11)

    def test_get_recipients_empty_event(self):
        self._init_events()
        form = SelectGroupForm({'group' : 'event_0'})

        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.get_selected_recipients()), 0)

    def test_get_recipients_event(self):
        self._init_users()
        self._init_events()
        self._init_events_attendees()
        preform = SelectGroupForm()
        form = SelectGroupForm({'group' : preform.fields['group'].widget.choices[1][0]})

        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.get_selected_recipients()), 5)

class MailModelTest(TestCase):
    def setUp(self):
        self.mailobj = Mail.objects.create(subject='test', body='test', date_created=date.today())

        self.users = []
        for i in range(10):
            user = auth_models.User.objects.create_user('user' + str(i), '', 'user' + str(i) + '@ex.ex')
            self.users.append(user)
            UserProfile.objects.create(user=user, dateofbirth=date.today(), send_me_email=True)

    def test_send_mail_single(self):
        self.mailobj.send_preview(['example@example.org',])

        self.assertEqual(len(mail.outbox), 1)

    def test_send_mail_multiple(self):
        self.mailobj.send_preview(['example@example.org', 'example2@example.org'])

        self.assertEqual(len(mail.outbox), 2)

    def test_send_mail_to_users(self):
        self.mailobj.send(self.users)

        self.assertEqual(len(mail.outbox), 10)
        self.assertEqual(len(self.mailobj.recipients.all()), 10)

    def test_filter(self):
        self.mailobj.send(self.users[:5])

        accept, deny = self.mailobj.recipient_filter(self.users)
        self.assertEqual(len(accept), 5)
        self.assertEqual(len(deny), 5)