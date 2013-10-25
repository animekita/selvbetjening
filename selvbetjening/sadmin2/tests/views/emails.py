
from django.core.urlresolvers import reverse
from django.test import TestCase

from mailqueue.models import MailerMessage

from selvbetjening.core.mailcenter.models import EmailSpecification


class EmailsTestCase(TestCase):

    fixtures = ['sdemo-example-site.json']

    def setUp(self):
        self.client.login(username='admin', password='admin')

    def test_emails_queue(self):
        response = self.client.get(reverse('sadmin2:emails_queue'))
        self.assertEqual(response.status_code, 200)

    def test_emails_templates(self):
        response = self.client.get(reverse('sadmin2:emails_templates'))
        self.assertEqual(response.status_code, 200)

    def test_emails_template(self):

        url = reverse('sadmin2:emails_template', kwargs={
            'template_pk': 1
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {
            'template_context': 'attendee',
            'subject': 'NewSubject',
            'body_format': 'markdown',
            'body': '...'
        }, follow=True)

        self.assertEqual(response.status_code, 200)

        self.assertTrue(EmailSpecification.objects.filter(subject='NewSubject').exists())

    def test_emails_template_preview(self):

        # TODO UI test selector

        url = reverse('sadmin2:emails_template_preview', kwargs={
            'template_pk': 1
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_emails_template_send(self):

        url = reverse('sadmin2:emails_template_send', kwargs={
            'template_pk': 1
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {
            'attendee_selector': 'Simple Event - user1 -   ()'
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(MailerMessage.objects.all().count(), 1)

    def test_emails_template_newsletter_users(self):

        url = reverse('sadmin2:emails_template_newsletter_users', kwargs={
            'template_pk': 1
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_emails_template_newsletter_users_correct_template(self):

        url = reverse('sadmin2:emails_template_newsletter_users', kwargs={
            'template_pk': 2
        })

        response = self.client.post(url, {
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(MailerMessage.objects.all().count(), 2)





