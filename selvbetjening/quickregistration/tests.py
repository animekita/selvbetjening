from django.contrib.auth import models as auth_models
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

import forms

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

class RegistrationFormTestCase(TestCase):
    def setUp(self):
        self.userData = get_user_data()

    def test_valid_user(self):
        form = forms.RegistrationForm(self.userData)

        self.assertTrue(form.is_valid())

    def test_invalid_username(self):
        self.userData['username'] = 'invalid usernames are cool!'
        form = forms.RegistrationForm(self.userData)

        self.assertFalse(form.is_valid())

    def test_duplicate_username(self):
        auth_models.User.objects.create_user('unittest_test', 'test@example.org', 'test')
        form = forms.RegistrationForm(self.userData)

        self.assertFalse(form.is_valid())

    def test_invalid_password_verify(self):
        self.userData['password2'] = 'testtesttest'
        form = forms.RegistrationForm(self.userData)

        self.assertFalse(form.is_valid())

    def test_invalid_empty_password(self):
        self.userData['password1'] = ''
        self.userData['password2'] = ''
        form = forms.RegistrationForm(self.userData)

        self.assertFalse(form.is_valid())

    def test_save(self):
        form = forms.RegistrationForm(self.userData)

        self.assertTrue(form.is_valid())
        user = form.save()

        test_user_created(self, user.username)

class ViewTestCase(TestCase):
    def setUp(self):
        self.user_data = get_user_data()

    def test_create_user(self):
        response = self.client.post(reverse('quickrregistration_register'), self.user_data)

        self.assertEqual(response.status_code, 302) # redirect

        test_user_created(self, "unittest_test")
