from django.contrib import admin

from models import RegistrationProfile

class RegistrationProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)

admin.site.register(RegistrationProfile, RegistrationProfileAdmin)