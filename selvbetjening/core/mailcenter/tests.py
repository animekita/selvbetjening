from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail

from selvbetjening.core.members.models import UserProfile

from models import EmailSpecification, UserConditions

class EmailSpecificationTest(TestCase):
    def setUp(self):
        self.users = []

        for i in range(10):
            user = User.objects.create_user('user' + str(i),
                                            '',
                                            'user' + str(i) + '@ex.ex')

            self.users.append(user)
            UserProfile.objects.create(user=user,
                                       dateofbirth=date.today(),
                                       send_me_email=True)

    def _send_email(self):
        mail.outbox = []

        from mailer.management.commands import send_mail
        command = send_mail.Command()
        command.handle_noargs()

    def test_send_email_single(self):
        email = EmailSpecification.objects.create(subject='test', body='test')

        email.send_email(self.users[0])
        self._send_email()

        self.assertEqual(len(mail.outbox), 1)

    def test_send_mail_multiple(self):
        email = EmailSpecification.objects.create(subject='test', body='test')

        email.send_email([self.users[0], self.users[1]])
        self._send_email()

        self.assertEqual(len(mail.outbox), 2)

    def test_get_conditions(self):
        email = EmailSpecification.objects.create(subject='test', body='test')

        conditions = email.conditions
        self.assertEqual(2, len(conditions))

    def test_filter_user_age(self):
        email = EmailSpecification.objects.create(subject='test', body='test')

        condition, created = UserConditions.objects.get_or_create(specification=email)

        condition.user_age_comparator = '<'
        condition.user_age_argument = 10
        condition.save()

        email.send_email(self.users[0])
        self._send_email()

        self.assertEqual(len(mail.outbox), 1)

        condition.user_age_comparator = '>'
        condition.save()

        email.send_email(self.users[0])
        self._send_email()

        self.assertEqual(len(mail.outbox), 0)