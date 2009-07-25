from django.contrib.auth import models as auth_models
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

def get_user_data():
    return {'username' : 'unittest_test',
            'password1' : 'test*',
            'password2' : 'test*',
            'first_name' : 'test',
            'last_name' : 'test',
            'email' : 'user@example.org',
            'dateofbirth' : '14-10-1987',
            'tos' : True}

def test_user_created(testcase, username):
    try:
        user = User.objects.get(username__exact=username)

        if user.get_profile() is None:
            testcase.fail("User profile not created")
    except User.DoesNotExist:
        testcase.fail("User object not created")

class ViewTestCase(TestCase):
    def setUp(self):
        self.user_data = get_user_data()

    def test_create_user(self):
        response = self.client.post(reverse('quickregistration_register'), self.user_data)

        self.assertEqual(response.status_code, 302) # redirect

        test_user_created(self, "unittest_test")
