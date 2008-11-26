from django.contrib.admin import AdminSite, ModelAdmin

from selvbetjening.events.models import Event

from models import EventmodeMachine

class EventAdmin(AdminSite):
    login_template = 'eventmode/login.html'

    def display_login_form(self, request, error_message='', extra_context=None):
        events = Event.objects.all()

        context = {
            'title': 'Login',
            'events' : events
            }
        context.update(extra_context or {})

        return super(EventAdmin, self).display_login_form(request, error_message, context)

site = EventAdmin()

class EventmodeMachineAdmin(ModelAdmin):
    list_display = ('event', 'name')

site.register(EventmodeMachine, EventmodeMachineAdmin)