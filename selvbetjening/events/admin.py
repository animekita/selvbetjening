from django.contrib import admin

from models import Event, Attend, Option, OptionGroup

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'startdate', 'enddate', 'registration_open')

admin.site.register(Event, EventAdmin)

class AttendAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'has_attended')

admin.site.register(Attend, AttendAdmin)

class OptionGroupAdmin(admin.ModelAdmin):
    list_display = ('event', 'name',)
    list_filter = ('event',)

admin.site.register(OptionGroup, OptionGroupAdmin)

class OptionAdmin(admin.ModelAdmin):
    list_display = ('group', 'name', 'attendees_count', 'freeze_time')
    list_filter = ('group',)

admin.site.register(Option, OptionAdmin)