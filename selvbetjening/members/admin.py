from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from models import UserProfile, EmailChangeRequest

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)

    fieldsets = (
        (None, {'fields' : ('user', 'dateofbirth', 'phonenumber', 'send_me_email')}),
        (_(u'Address'), {'classes': ('collapse',), 'fields' : ('street', 'postalcode', 'city')}),
    )

admin.site.register(UserProfile, UserProfileAdmin)

class EmailChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'new_email', 'timestamp')

admin.site.register(EmailChangeRequest, EmailChangeRequestAdmin)