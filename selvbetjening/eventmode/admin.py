from django.contrib.admin import ModelAdmin

class EventmodeMachineAdmin(ModelAdmin):
    list_display = ('event', 'name')
