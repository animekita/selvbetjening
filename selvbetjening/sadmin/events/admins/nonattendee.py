# -- encoding: utf-8 --

from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from selvbetjening.core.events.models import Event

from selvbetjening.sadmin.base.sadmin import SBoundModelAdmin
from selvbetjening.sadmin.events import nav

def add_to_event_action(self, request, queryset):
    for user in queryset:
        request.bound_object.add_attendee(user)
add_to_event_action.short_description = _(u'Add as attendee to event')

class NonAttendeeAdmin(SBoundModelAdmin):
    class Meta:
        app_name = 'events'
        name = 'nonattendee'
        model = User
        bound_model = Event
        default_views = ('list',)

    list_display_links = ('',)
    list_per_page = 50
    list_display = ('username', 'first_name', 'last_name')
    search_fields = ('username', 'first_name', 'last_name')
    actions = [add_to_event_action,]

    def queryset(self, request):
        qs = super(SBoundModelAdmin, self).queryset(request)
        return qs.exclude(attend__event=request.bound_object)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['menu'] = nav.event_menu.render(event_pk=request.bound_object.pk)
        extra_context['title'] = _(u'Add attendee')
        return super(NonAttendeeAdmin, self).changelist_view(request, extra_context)