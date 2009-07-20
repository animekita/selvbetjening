from django.utils.translation import ugettext as _
from django.contrib.admin import ModelAdmin, TabularInline
from django.contrib.auth.models import User

from models import Attend, Option, OptionGroup, SubOption, Selection

class AttendAdmin(ModelAdmin):
    list_display = ('user', 'event', 'has_attended', 'dispaly_has_paid')
    list_filter = ('event',)
    
    def dispaly_has_paid(self, attend):
        return attend.invoice.is_paid()
    dispaly_has_paid.boolean = True

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

class OptionInline(TabularInline):
    model = Option
    exclude = ['users', ]

class OptionGroupAdmin(ModelAdmin):
    list_display = ('event', 'name',)
    list_filter = ('event',)

    fieldsets = (
        (None, {
            'fields' : ('event', 'name', 'description'),
        }),
        (_('Conditions'), {
            'fields' : ('minimum_selected', 'maximum_selected', 'maximum_attendees', 'freeze_time'),
            'classes' : ('collapse', ),
        }),
        (_('Other'), {
            'fields' : ('order',),
        }),)
    
    inlines = [OptionInline, ]

class SubOptionInline(TabularInline):
    model = SubOption
    
class SelectionInline(TabularInline):
    model = Selection
    
class OptionAdmin(ModelAdmin):
    list_display = ('group', 'name', 'attendee_count', 'freeze_time')
    list_filter = ('group',)
    fieldsets = (
        (None, {'fields': ('group', 'name', 'description', 'price')}),
        ('Conditions', {'fields': ('freeze_time', 'maximum_attendees', 'order'), 'classes' : ('collapse',)}),
        )
    
    inlines = [SubOptionInline, SelectionInline]

