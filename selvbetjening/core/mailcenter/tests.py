
from django.test import TestCase
from django.core import mail
from selvbetjening.core.mailcenter.models import EmailSpecification

from selvbetjening.core.user.models import SUser


class EmailSendingTestCase(TestCase):
    fixtures = ['sdemo-example-site.json']

    def test_check(self):
        obj = EmailSpecification.objects.create(
            subject='TEST',
            body='TEST')

        self.assertIsNotNone(obj)

        obj.send_email_user(SUser.objects.get(pk=1), 'TEST')
        self.assertEqual(len(mail.outbox), 0)

        obj.body = '{% url DUMMY %}'  # invalid body
        obj.save()

        obj.send_email_user(SUser.objects.get(pk=1), 'TEST')
        self.assertEqual(len(mail.outbox), 1)
