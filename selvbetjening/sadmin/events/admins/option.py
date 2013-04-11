from django.contrib.admin import TabularInline, StackedInline
from django.utils.translation import ugettext as _

from selvbetjening.core.events.models import Option, OptionGroup, SubOption, Selection

from selvbetjening.sadmin.base.admin import TranslationInline
from selvbetjening.sadmin.base.sadmin import SBoundModelAdmin


class SubOptionInline(StackedInline):
    model = SubOption
    extra = 0


class SelectionInline(TabularInline):
    model = Selection
    extra = 0

    raw_id_fields = ('attendee',)


class OptionAdmin(SBoundModelAdmin):
    depth = 2

    class Meta:
        app_name = 'events'
        name = 'option'
        model = Option
        bound_model = OptionGroup
        bind_key = 'bind_bind_pk'

        display_name = _(u'Option')
        display_name_plural = _(u'Options')

    def attendees_count(option):
        return option.selections.count()

    list_display = ('name', attendees_count, 'freeze_time')

    fieldsets = (
        (None, {'fields': ('name', 'description', 'price')}),
        ('Conditions', {
            'fields': ('freeze_time', 'maximum_attendees', 'order'),
            'classes' : ('collapse',)
        }),
    )

    raw_id_fields = ('group',)
    inlines = [SubOptionInline, TranslationInline, SelectionInline]

    def queryset(self, request):
        qs = super(OptionAdmin, self).queryset(request)
        return qs.filter(group=request.bound_object)

    def _get_navigation_stack(self, request):
        return [request.bound_object.event, request.bound_object,]

    def change_view(self, request, object_id, extra_context=None, **kwargs):
        return super(OptionAdmin, self).change_view(request, object_id, extra_context)

    def changelist_view(self, request, extra_context=None, **kwargs):
        return super(OptionAdmin, self).changelist_view(request, extra_context)

    def add_view(self, request, extra_context=None, **kwargs):
        return super(OptionAdmin, self).add_view(request, extra_context=extra_context)

    def delete_view(self, request, object_id, extra_context=None, **kwargs):
        return super(OptionAdmin, self).delete_view(request, object_id, extra_context)

    def save_form(self, request, form, change):
        instance = form.save(commit=False)

        if not change:
            instance.group = request.bound_object

        return instance