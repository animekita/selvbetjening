from django.utils.translation import ugettext as _

from selvbetjening.core.events.models import OptionGroup, Event

from selvbetjening.sadmin.base.sadmin import SBoundModelAdmin

from selvbetjening.sadmin.events.admins.option import OptionAdmin
from selvbetjening.sadmin.events import nav

class OptionGroupAdmin(SBoundModelAdmin):
    class Meta:
        app_name = 'events'
        name = 'optiongroup'
        model = OptionGroup
        bound_model = Event

    list_display = ('name',)

    fieldsets = (
        (None, {
            'fields' : ('event', 'name', 'description'),
            }),
        (_('Conditions'), {
            'fields' : ('minimum_selected', 'maximum_selected', 'maximum_attendees', 'freeze_time'),
            'classes' : ('collapse', ),
            }),
        (_('Other'), {
            'fields' : ('order', 'public_statistic',),
            }),)

    def queryset(self, request):
        qs = super(OptionGroupAdmin, self).queryset(request)
        return qs.filter(event=request.bound_object)

    def get_urls(self):
        from django.conf.urls.defaults import patterns, include

        urlpattern = super(OptionGroupAdmin, self).get_urls()

        urlpattern = patterns('',
            (r'^(?P<bind_optiongroup_pk>.+)/options/', include(OptionAdmin().urls)),
        ) + urlpattern

        return urlpattern

    def add_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['menu'] = nav.event_menu.render(event_pk=request.bound_object.pk)
        return super(OptionGroupAdmin, self).add_view(request, extra_context=extra_context)
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['menu'] = nav.event_menu.render(event_pk=request.bound_object.pk)

        return super(OptionGroupAdmin, self).changelist_view(request, extra_context)

    def change_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        extra_context['menu'] = nav.optiongroup_menu.render(event_pk=request.bound_object.pk,
                                                            optiongroup_pk=object_id)

        return super(OptionGroupAdmin, self).change_view(request, object_id, extra_context)
