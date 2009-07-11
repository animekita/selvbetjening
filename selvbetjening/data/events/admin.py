from django.utils.translation import ugettext as _
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
    fieldsets = (
        (None, {
            'fields' : ('title', 'description', 'startdate', 'enddate', 'registration_open'),
        }),
        (_('Conditions'), {
            'fields' : ('maximum_attendees',),
            'classes' : ('collapse', ),
        }),
        (_('Registration Confirmation'), {
            'fields' : ('show_registration_confirmation', 'registration_confirmation'),
            'classes' : ('collapse', ),
        }),
        (_('Change Confirmation'), {
            'fields' : ('show_change_confirmation', 'change_confirmation'),
            'classes' : ('collapse', ),
        }),
    )
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
        (None, {'fields': ('group', 'name', 'description', 'price')}),
        ('Conditions', {'fields': ('freeze_time', 'maximum_attendees', 'order'), 'classes' : ('collapse',)}),
        ('Users', {'fields': ('users',), 'classes': ('collapse',)}),
        )

