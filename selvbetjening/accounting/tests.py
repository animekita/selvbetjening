from datetime import datetime, timedelta

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import models as auth_models
from django.core.urlresolvers import reverse

from selvbetjening.members.models import UserProfile

import models
import forms

class AccountingPaymentFormTestCase(TestCase):

    def setUp(self):
        self.user1 = auth_models.User.objects.create_user('user1', 'user1', 'user@example.org')

    def test_valid_options(self):
        f = forms.PaymentForm({'type' : 'FULL'}, user=self.user1)

        self.assertTrue(f.is_valid())

    def test_impossible_option(self):
        f = forms.PaymentForm({'type' : 'SRATE'}, user=self.user1)

        self.assertFalse(f.is_valid())

    def test_invalid_option(self):
        f = forms.PaymentForm({'type' : 'DOH'}, user=self.user1)

        self.assertFalse(f.is_valid())

    def test_save(self):
        f = forms.PaymentForm({'type' : 'FULL'}, user=self.user1)
        self.assertTrue(f.is_valid())
        f.save()

        self.assertEqual(1, len(self.user1.payment_set.all()))

class AccountingModelTestCase(TestCase):

    def setUp(self):
        self.date_inactive = datetime(datetime.now().year - 2, datetime.now().month, datetime.now().day)
        self.date_passive = datetime(datetime.now().year - 1, datetime.now().month, datetime.now().day)
        self.date_active = datetime.now()

        self.user1 = auth_models.User.objects.create_user('user1', 'user1', 'user@example.org')
        self.user2 = auth_models.User.objects.create_user('user2', 'user2', 'user@example.org')
        self.user2.payment_set.create(type='FULL', timestamp=self.date_inactive)
        self.user3 = auth_models.User.objects.create_user('user3', 'user3', 'user@example.org')
        self.user3.payment_set.create(type='FULL', timestamp=self.date_passive)
        self.user4 = auth_models.User.objects.create_user('user4', 'user4', 'user@example.org')
        self.user4.payment_set.create(type='FULL', timestamp=self.date_active)

        self.user5 = auth_models.User.objects.create_user('user5', 'user5', 'user@example.org')
        self.user5.payment_set.create(type='FRATE', timestamp=self.date_inactive)
        self.user6 = auth_models.User.objects.create_user('user6', 'user6', 'user@example.org')
        self.user6.payment_set.create(type='FRATE', timestamp=self.date_passive)
        self.user7 = auth_models.User.objects.create_user('user7', 'user7', 'user@example.org')
        self.user7.payment_set.create(type='FRATE', timestamp=self.date_active)

        self.user8 = auth_models.User.objects.create_user('user8', 'user8', 'user@example.org')
        self.user8.payment_set.create(type='FRATE', timestamp=self.date_inactive)
        self.user8.payment_set.create(type='SRATE', timestamp=self.date_inactive + timedelta(minutes=1))
        self.user9 = auth_models.User.objects.create_user('user9', 'user9', 'user@example.org')
        self.user9.payment_set.create(type='FRATE', timestamp=self.date_passive)
        self.user9.payment_set.create(type='SRATE', timestamp=self.date_passive + timedelta(minutes=1))
        self.user10 = auth_models.User.objects.create_user('user10', 'user10', 'user@example.org')
        self.user10.payment_set.create(type='FRATE', timestamp=self.date_active)
        self.user10.payment_set.create(type='SRATE', timestamp=self.date_active + timedelta(minutes=1))

    def test_no_payments(self):
        self.assertEqual(models.MembershipState.INACTIVE,
                         models.Payment.objects.get_membership_state(self.user1))

    def test_full_payment_inactive(self):
        self.assertEqual(models.MembershipState.INACTIVE,
                         models.Payment.objects.get_membership_state(self.user2))

    def test_full_payment_passive(self):
        self.assertEqual(models.MembershipState.PASSIVE,
                         models.Payment.objects.get_membership_state(self.user3))

    def test_full_payment_active(self):
        self.assertEqual(models.MembershipState.ACTIVE,
                         models.Payment.objects.get_membership_state(self.user4))

    def test_frate_payment_inactive(self):
        self.assertEqual(models.MembershipState.INACTIVE,
                         models.Payment.objects.get_membership_state(self.user5))

    def test_frate_payment_passive(self):
        self.assertEqual(models.MembershipState.PASSIVE,
                         models.Payment.objects.get_membership_state(self.user6))

    def test_frate_payment_condactive(self):
        self.assertEqual(models.MembershipState.CONDITIONAL_ACTIVE,
                         models.Payment.objects.get_membership_state(self.user7))

    def test_srate_payment_inactive(self):
        self.assertEqual(models.MembershipState.INACTIVE,
                         models.Payment.objects.get_membership_state(self.user8))

    def test_srate_payment_passive(self):
        self.assertEqual(models.MembershipState.PASSIVE,
                         models.Payment.objects.get_membership_state(self.user9))

    def test_srate_payment_active(self):
        self.assertEqual(models.MembershipState.ACTIVE,
                         models.Payment.objects.get_membership_state(self.user10))
