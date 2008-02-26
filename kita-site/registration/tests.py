from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import models as auth_models
from django.test import TestCase
from django.core import mail

from registration import forms
from registration import models

class RegistartionModelTestCase(TestCase):
    def setUp(self):
        self.user = auth_models.User.objects.create_user('user', 'user', 'user@example.org')
    
    def test_activationkey_not_expired(self):
        rp = models.RegistrationProfile.objects.create_registration_profile(user = self.user, forumPassword = 'ddd')
        
        self.assertFalse(rp.activation_key_expired())
    
    def test_activationkey_expired(self):
        self.user.date_joined = datetime.now() - timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS, minutes = 1)
        self.user.save()
        
        rp = models.RegistrationProfile.objects.create_registration_profile(user = self.user, forumPassword = 'ddd')
        
        self.assertTrue(rp.activation_key_expired())
        
    def test_create_inactive_user(self):
        u = models.RegistrationProfile.objects.create_inactive_user('newuser', 'newuser', 'newuser@example.org', datetime.now(), 'newuser', 'newuser', 'd', 'd', '9000', '12121212', True)
        
        # check for registration profile
        try:
            models.RegistrationProfile.objects.get(user=u)
        except models.RegistrationProfile.DoesNotExist:
            self.fail(msg = 'Registration Profile not created')
        
        # check for user profile
        try:
            p = u.get_profile()
        except auth_models.SiteProfileNotAvailable:
            self.fail(msg = 'Profile not created')        
        
        # check for registration email
        self.assertEqual(len(mail.outbox), 1)
    
    def test_activate_user(self):
        u = models.RegistrationProfile.objects.create_inactive_user('newuser', 'newuser', 'newuser@example.org', datetime.now(), 'newuser', 'newuser', 'd', 'd', '9000', '12121212', True)
        
        p = models.RegistrationProfile.objects.get(user=u)
        
        self.assertEquals(u, models.RegistrationProfile.objects.activate_user(p.activation_key))
    
    def test_activate_nonexisting_user(self):
        self.assertEqual(models.RegistrationProfile.objects.activate_user(''), None)
    
    def test_create_user(self):
        u = models.RegistrationProfile.objects.create_user('newuser', 'newuser', 'newuser@example.org', datetime.now(), 'newuser', 'newuser', 'd', 'd', '9000', '12121212', True)
        
        self.assertTrue(isinstance(u, auth_models.User))
        
        self.assertTrue(u.is_active)
        
        try:
            p = u.get_profile()
        except auth_models.SiteProfileNotAvailable:
            self.fail(msg = 'Profile not created')

class RegistrationFormTestCase(TestCase):
    def setUp(self):
        self.userData = {'username' : 'unittest_test', 
                        'password1' : 'test*', 
                        'password2' : 'test*', 
                        'first_name' : 'test',
                        'last_name' : 'test',
                        'email' : 'user@example.org', 
                        'dateofbirth' : '14-10-1987',
                        'tos' : True,}
    
    def test_valid_user(self):
        form = forms.RegistrationForm(self.userData)
        
        self.assertTrue(form.is_valid())
    
    def test_invalid_username(self):
        self.userData['username'] = 'invalid usernames are cool!'
        form = forms.RegistrationForm(self.userData)
        
        self.assertFalse(form.is_valid())
    
    def testDuplicateUsername(self):
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
        
        try:
            models.RegistrationProfile.objects.get(user=user)
        except models.RegistrationForm.DoesNotExist:
            self.fail(msg = 'Registration profile were not created')
