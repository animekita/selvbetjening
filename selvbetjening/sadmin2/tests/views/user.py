from django.core.urlresolvers import reverse
from django.test import TestCase

from selvbetjening.core.user.models import SUser


class UserTestCase(TestCase):

    fixtures = ['sdemo-example-site.json']

    def setUp(self):
        self.client.login(username='admin', password='admin')

    def test_user(self):
        url = reverse('sadmin2:user', kwargs={'user_pk': 1})  # admin user

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {
            'username': 'admin',
            'first_name': 'John',
            'last_name': 'Doe'
        }, follow=True)

        self.assertEqual(response.status_code, 200)

        user = SUser.objects.get(pk=1)
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')

    def test_user_password(self):
        url = reverse('sadmin2:user_password', kwargs={'user_pk': 1})  # admin user

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {
            'password1': '1234',
            'password2': '1234'
        }, follow=True)

        self.assertEqual(response.status_code, 200)

        self.assertTrue(self.client.login(username='admin', password='1234'))
        self.assertFalse(self.client.login(username='admin', password='admin'))

