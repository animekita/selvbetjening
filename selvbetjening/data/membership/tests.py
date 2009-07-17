from datetime import datetime, timedelta

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import models as auth_models
from django.core.urlresolvers import reverse

from selvbetjening.data.members.models import UserProfile

import forms
from  membership_controller import MembershipController

MembershipController._choices = [{'id' : 'FULL', 'description' : 'test'},
                                 {'id' : 'FRATE', 'description' : 'test'}]

class MembershipFormTestCase(TestCase):

    def setUp(self):
        self.user1 = auth_models.User.objects.create_user('user1', 'user1', 'user@example.org')

    def test_valid_options(self):
        f = forms.MembershipForm({'type' : 'FULL'}, user=self.user1)

        self.assertTrue(f.is_valid())

    def test_invalid_option(self):
        f = forms.MembershipForm({'type' : 'DOH'}, user=self.user1)

        self.assertFalse(f.is_valid())

    def test_save(self):
        f = forms.MembershipForm({'type' : 'FULL'}, user=self.user1)
        self.assertTrue(f.is_valid())
        f.save()

        self.assertTrue(MembershipController.is_member(self.user1))
        

