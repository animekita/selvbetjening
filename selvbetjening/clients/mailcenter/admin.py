from django.contrib import admin

from models import Mail

class MailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'date_created', 'is_draft')
    search_fields = ('subject',)
