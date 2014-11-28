
from django.test import TestCase
from selvbetjening.businesslogic.members.forms import ProfileEditForm
from selvbetjening.core.user.models import SUser
from selvbetjening.settings_base import POLICY


class MemberEditFormTestCase(TestCase):

    def setUp(self):
        self.user = SUser.objects.create(
            username='testuser'
        )

    def test_form_validation_base(self):

        # Empty is not allowed
        form = ProfileEditForm({}, instance=self.user)
        self.assertFalse(form.is_valid())

        # first and last name is required by default
        form = ProfileEditForm({
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'example@example.org'
        }, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_form_validation_location_policy(self):

        POLICY['VALIDATION.USER_LOCATION.REQUIRED'] = True

        try:

            form = ProfileEditForm({
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'example@example.org'
            }, instance=self.user)
            self.assertFalse(form.is_valid())

            form = ProfileEditForm({
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'example@example.org',
                'street': 'LANE',
                'postalcode': 9000,
                'city': 'VILLE',
                'country': 'DK'
            }, instance=self.user)
            self.assertTrue(form.is_valid())

        finally:
            POLICY['VALIDATION.USER_LOCATION.REQUIRED'] = False