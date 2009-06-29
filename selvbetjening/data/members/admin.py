from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.admin import ModelAdmin, StackedInline
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from shortcuts import get_or_create_profile

from models import UserProfile

class UserProfileInline(StackedInline):
    model = UserProfile
    extra = 1
    max_num = 1

class UserAdminExt(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'display_age')

    def display_age(self, user):
        user_profile = get_or_create_profile(user)
        age = user_profile.get_age()
        return age
    display_age.admin_order_field = 'userprofile__dateofbirth'
    display_age.short_description = 'age'
