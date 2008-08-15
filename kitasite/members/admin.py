from django.contrib import admin

from models import UserProfile, EmailChangeRequest

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)

admin.site.register(UserProfile, UserProfileAdmin)

class EmailChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'new_email', 'timestamp')

admin.site.register(EmailChangeRequest, EmailChangeRequestAdmin)