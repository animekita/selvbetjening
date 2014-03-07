from django.core.urlresolvers import reverse
from django.test import TestCase
from django.contrib.auth.models import Group

from selvbetjening.core.user.models import SUser


class UsersTestCase(TestCase):

    fixtures = ['sdemo-example-site.json']

    def setUp(self):
        self.client.login(username='admin', password='admin')

    def test_users(self):
        response = self.client.get(reverse('sadmin2:users_list'))
        self.assertEqual(response.status_code, 200)

    def test_users_create(self):
        url = reverse('sadmin2:users_create')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.client.post(url, {
            'username': 'johndoe'
        })

        self.assertTrue(SUser.objects.filter(username='johndoe').exists())

    def test_users_groups(self):
        response = self.client.get(reverse('sadmin2:users_groups_list'))
        self.assertEqual(response.status_code, 200)

    def test_users_groups_create(self):
        url = reverse('sadmin2:users_groups_create')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.client.post(url, {
            'name': 'Group1'
        })

        self.assertTrue(Group.objects.filter(name='Group1').exists())

    def test_group(self):
        url = reverse('sadmin2:users_group', kwargs={'group_pk': 1})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {
            'name': 'GroupAlt',
        }, follow=True)

        self.assertEqual(response.status_code, 200)

        self.assertTrue(Group.objects.filter(name='GroupAlt').exists())

    def test_users_reports_users(self):

        response = self.client.get(reverse('sadmin2:users_reports_users'))
        self.assertEqual(response.status_code, 200)

    def test_users_reports_age(self):

        response = self.client.get(reverse('sadmin2:users_reports_age'))
        self.assertEqual(response.status_code, 200)

    def test_users_reports_address(self):

        response = self.client.get(reverse('sadmin2:users_reports_address'))
        self.assertEqual(response.status_code, 200)