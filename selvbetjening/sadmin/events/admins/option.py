from django.contrib.admin import TabularInline

from selvbetjening.core.events.models import Option, OptionGroup, SubOption, Selection
from selvbetjening.core.translation.admin import TranslationInline

from selvbetjening.sadmin.base.sadmin import SBoundModelAdmin
from selvbetjening.sadmin.events import nav

class SubOptionInline(TabularInline):
    model = SubOption

class SelectionInline(TabularInline):
    model = Selection

    raw_id_fields = ('attendee',)

class OptionAdmin(SBoundModelAdmin):
    class Meta:
        app_name = 'events'
        name = 'option'
        model = Option
        bound_model = OptionGroup
        bind_key = 'bind_optiongroup_pk'

    def attendees_count(option):
        return option.selections.count()

    list_display = ('name', attendees_count, 'freeze_time')

    fieldsets = (
        (None, {'fields': ('group', 'name', 'description', 'price')}),
        ('Conditions', {
            'fields': ('freeze_time', 'maximum_attendees', 'order'),
            'classes' : ('collapse',)
        }),
    )

    raw_id_fields = ('group',)
    inlines = [SubOptionInline, SelectionInline, TranslationInline]

    def queryset(self, request):
        qs = super(OptionAdmin, self).queryset(request)
        return qs.filter(group=request.bound_object)

    def change_view(self, request, object_id, extra_context=None, **kwargs):
        return super(OptionAdmin, self).change_view(request, object_id, extra_context)

    def changelist_view(self, request, extra_context=None, **kwargs):
        extra_context = extra_context or {}
        extra_context['menu'] = nav.optiongroup_menu.render(event_pk=request.bound_object.event.pk,
                                                            optiongroup_pk=request.bound_object.pk)

        return super(OptionAdmin, self).changelist_view(request, extra_context)

    def add_view(self, request, extra_context=None, **kwargs):
        return super(OptionAdmin, self).add_view(request, extra_context)

    def delete_view(self, request, object_id, extra_context=None, **kwargs):
        return super(OptionAdmin, self).delete_view(request, object_id, extra_context)
