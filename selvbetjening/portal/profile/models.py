from django.db import models
from django.contrib.auth.models import User

class UserPrivacy(models.Model):
    user = models.ForeignKey(User)

    public_profile = models.BooleanField(default=False)

    public_name = models.BooleanField(default=False)
    public_age = models.BooleanField(default=False)
    public_sex = models.BooleanField(default=False)
    public_email = models.BooleanField(default=False)
    public_phonenumber = models.BooleanField(default=False)
    public_town = models.BooleanField(default=False)

    public_contact = models.BooleanField(default=False)
    public_websites = models.BooleanField(default=False)

    public_join_date = models.BooleanField(default=False)

    @staticmethod
    def full_access():
        privacy = UserPrivacy()
        privacy.public_profile = True
        privacy.public_name = True
        privacy.public_age = True
        privacy.public_sex = True
        privacy.public_email = True
        privacy.public_phonenumber = True
        privacy.public_town = True
        privacy.public_contact = True
        privacy.public_websites = True
        privacy.public_achievements = True
        privacy.public_join_date = True

        return privacy
