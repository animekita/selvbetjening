from django.contrib.admin import StackedInline

from models import UserProfile

class UserProfileInline(StackedInline):
    model = UserProfile
    extra = 1
    max_num = 1
