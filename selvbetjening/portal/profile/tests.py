from django import test

from models import UserPrivacy

class UserPrivacyTestCase(test.TestCase):
    def test_full_access_privacy(self):
        privacy = UserPrivacy.full_access()
        self.assertTrue(privacy.public_profile)
        self.assertTrue(privacy.public_age)

    def test_partial_access(self):
        privacy = UserPrivacy()

        privacy.public_profile = True
        privacy.public_age = True

        self.assertTrue(privacy.public_age)
        self.assertFalse(privacy.public_name)