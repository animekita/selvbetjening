from django.core.exceptions import ObjectDoesNotExist

from models import UserProfile


def get_or_create_profile(user):
    try:
        profiles = user.userprofile_set.all()
        return profiles[0] if len(profiles) > 0 else UserProfile.objects.create(user=user)
    except ObjectDoesNotExist:
        return UserProfile.objects.create(user=user)