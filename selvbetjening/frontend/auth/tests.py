from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse
from django.test import TestCase
from mailqueue.models import MailerMessage
import re


class FrontendAuthTestCase(TestCase):

    fixtures = ['sdemo-example-site.json']

    def test_password_recovery(self):
        response = self.client.get(reverse('auth_password_reset'))

        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('auth_password_reset'), {
            'email': 'example@example.org'
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(MailerMessage.objects.all().count(), 1)

        mail_content = MailerMessage.objects.all()[0].content
        regex = re.compile('https?://\w+\.\w+(/[\w/\-]+/)')
        match = regex.search(mail_content)

        self.assertIsNotNone(match)

        response = self.client.get(match.group(1))

        self.assertEqual(response.status_code, 200)

        response = self.client.post(match.group(1), {
            'new_password1': '1234',
            'new_password2': '1234'
        })

        self.assertEqual(response.status_code, 302)

        user = authenticate(username='admin', password='1234')
        self.assertIsNotNone(user)
