from django.core.exceptions import ObjectDoesNotExist

from models import UserProfile

def get_or_create_profile(user):
    try:
        return user.get_profile()
    except ObjectDoesNotExist:
        return UserProfile.objects.create(user=user)