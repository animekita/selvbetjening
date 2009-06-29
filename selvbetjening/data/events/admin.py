from django.contrib.admin import ModelAdmin, TabularInline
from django.contrib.auth.models import User

from models import Attend, Option, OptionGroup

class AttendInline(TabularInline):
    model = Attend
    raw_id_fields = ('user',)
    verbose_name = 'Deltager'
    verbose_name_plural = 'Deltagere'

class EventAdmin(ModelAdmin):
    list_display = ('title', 'startdate', 'enddate', 'registration_open')
    inlines = [AttendInline, ]

class OptionInline(TabularInline):
    model = Option
    exclude = ['users', ]

class OptionGroupAdmin(ModelAdmin):
    list_display = ('event', 'name',)
    list_filter = ('event',)

    inlines = [OptionInline, ]

class OptionAdmin(ModelAdmin):
    list_display = ('group', 'name', 'attendees_count', 'freeze_time')
    list_filter = ('group',)
    raw_id_fields = ('users',)
    fieldsets = (
        (None, {'fields': ('group', 'name', 'description')}),
        ('Conditions', {'fields': ('freeze_time', 'maximum_attendees', 'order'), 'classes' : ('collapse',)}),
        ('Users', {'fields': ('users',), 'classes': ('collapse',)}),
        )

