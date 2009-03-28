from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import User

from models import ExtendedUser, UserProfile

class ExtendedUserAdmin(ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'get_age')

    fieldsets = (
        (None, {'fields': ('username', 'first_name', 'last_name', 'dateofbirth',)}),
        (_('Contact'), {'fields': ('email', 'send_me_email', 'phonenumber'), 'classes': ['collapse',]}),
        (_('Address'), {'fields': ('street', 'city', 'postalcode',), 'classes': ['collapse',]}),
        (_('Password'), {'fields': ('password',), 'classes': ['collapse',]}),
        (_('Permissions'), {'fields': ('is_staff', 'is_active', 'is_superuser', 'user_permissions'),
                            'classes': ['collapse',]}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined'),
                                'classes': ['collapse',]}),
        (_('Groups'), {'fields': ('groups',), 'classes': ['collapse',]}),
    )

    list_filter = ('is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    inlines = []

    def check_integrity(self, request, queryset):
        users_without_profiles = User.objects.filter(userprofile=None)
        for user in users_without_profiles:
            UserProfile.objects.create(user=user)

        if len(users_without_profiles) == 1:
            message_bit = 'one user was'
        elif len(users_without_profiles) > 1:
            message_bit = '%s new users where' % len(users_without_profiles)
        else:
            message_bit = 'no users where'

        self.message_user(request, '%s recovered' % message_bit)

    actions = ['check_integrity']
