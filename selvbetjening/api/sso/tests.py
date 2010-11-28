from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse

from selvbetjening.core.events.tests import Database as EventDatabase

class VerifyTestCase(TestCase):
    def test_invalid_sessionid(self):
        url = reverse('api_sso_validate',
                      kwargs = {'service' : 'test',
                                'auth_token' : 'fake_auth_token'})

        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, u'rejected')

    def test_valid_sessionid(self):
        user = EventDatabase.new_user(id='test')
        self.client.login(username='test', password='test')

        auth_token = self.client.cookies.get(settings.SESSION_COOKIE_NAME).value

        url = reverse('api_sso_validate',
                      kwargs = {'service' : 'test',
                                'auth_token' : auth_token})

        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, u'accepted/test')

class InfoTestCase(TestCase):
    def test_info_no_login(self):
        url = reverse('api_sso_info',
                      kwargs = {'service' : 'test',
                                'auth_token' : 'fake_auth_token'})

        resp = self.client.get(url)

        self.assertContains(resp, '<success>False</success>')

    def test_info(self):
        user = EventDatabase.new_user(id='test')
        self.client.login(username='test', password='test')

        auth_token = self.client.cookies.get(settings.SESSION_COOKIE_NAME).value

        url = reverse('api_sso_info',
                      kwargs = {'service' : 'test',
                                'auth_token' : auth_token})

        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(user.username in resp.content)
        self.assertTrue(user.first_name in resp.content)
        self.assertTrue(user.last_name in resp.content)
        self.assertTrue(user.email in resp.content)