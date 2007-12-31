from django.conf import settings
from django.contrib.auth import models as auth_models
from django.test import TestCase
from django.core import mail

from migration import forms
from registration import models

class MigrationFormTestCase(TestCase):
    def setUp(self):
        self.userData = {'username' : 'unittest_test', 
                         'password1' : 'test*', 
                         'password2' : 'test*', 
                         'first_name' : 'test',
                         'last_name' : 'test',
                         'email' : 'user@example.org', 
                         'dateofbirth' : '14-10-1987',
                         'tos' : True,}
        
        self.currentUser = 'unittest_test'
    
    def testValidUser(self):
        form = forms.MigrationForm(self.userData, user=self.currentUser)
        
        self.assertTrue(form.is_valid())
    
    def testSave(self):
        form = forms.MigrationForm(self.userData, user=self.currentUser)
        
        self.assertTrue(form.is_valid())
        user = form.save()
        
        try:
            models.RegistrationProfile.objects.get(user=user)
        except models.RegistrationProfile.DoesNotExist:
            self.fail(msg = 'Registration profile was not created')