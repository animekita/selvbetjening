from django.contrib.auth import models as auth_models
from django.test import TestCase

from selvbetjening.core.user.models import SUser
from selvbetjening.core.events.tests import Database as EventDatabase

import signals

def get_user_data():
    return {'username' : 'unittest_test',
            'password1' : 'test*',
            'password2' : 'test*',
            'first_name' : 'test',
            'last_name' : 'test',
            'email' : 'user@example.org',
            'dateofbirth' : '14.10.1987',
            'country' : 'DK',
            'send_me_email' : False,
            'tos' : True}

def test_user_created(testcase, username):
    try:
        user = SUser.objects.get(username__exact=username)

        if user.get_profile() is None:
            testcase.fail('User profile not created')
    except SUser.DoesNotExist:
        testcase.fail('User object not created')

class RegistrationFormTestCase(TestCase):
    def setUp(self):
        self.userData = get_user_data()

    def test_valid_user(self):
        import forms
        form = forms.RegistrationForm(self.userData)

        self.assertTrue(form.is_valid())

    def test_invalid_username(self):
        import forms
        self.userData['username'] = 'invalid usernames are cool!'
        form = forms.RegistrationForm(self.userData)

        self.assertFalse(form.is_valid())

    def test_duplicate_username(self):
        import forms
        auth_models.User.objects.create_user('unittest_test', 'test@example.org', 'test')
        form = forms.RegistrationForm(self.userData)

        self.assertFalse(form.is_valid())

    def test_invalid_password_verify(self):
        import forms
        self.userData['password2'] = 'testtesttest'
        form = forms.RegistrationForm(self.userData)

        self.assertFalse(form.is_valid())

    def test_invalid_empty_password(self):
        import forms
        self.userData['password1'] = ''
        self.userData['password2'] = ''
        form = forms.RegistrationForm(self.userData)

        self.assertFalse(form.is_valid())

    def test_save(self):
        import forms
        form = forms.RegistrationForm(self.userData)

        self.assertTrue(form.is_valid())
        user = form.save()

        test_user_created(self, user.username)

class SignalsTestCase(TestCase):
    def test_change_password_non_ascii(self):
        user = EventDatabase.new_user()
        user.set_password(u'abc\xf8')
