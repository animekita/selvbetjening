from django.contrib.admin import AdminSite, ModelAdmin

from selvbetjening.events.models import Event

from models import EventmodeMachine

class EventmodeMachineAdmin(ModelAdmin):
    list_display = ('event', 'name')
