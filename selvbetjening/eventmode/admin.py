from django.contrib import admin

from models import Eventmode

class EventmodeAdmin(admin.ModelAdmin):
    list_display = ('event',)

admin.site.register(Eventmode, EventmodeAdmin)