from django.utils.translation import ugettext as _

from selvbetjening.core.events.models import OptionGroup, Event

from selvbetjening.sadmin.base.sadmin import SBoundModelAdmin

from selvbetjening.sadmin.base.admin import TranslationInline
from selvbetjening.sadmin.events.admins.option import OptionAdmin

class OptionGroupAdmin(SBoundModelAdmin):
    class Meta:
        app_name = 'events'
        name = 'optiongroup'
        model = OptionGroup
        bound_model = Event
        display_name = _(u'Option Group')
        display_name_plural = _(u'Option Groups')

    list_display = ('name',)

    fieldsets = (
        (None, {
            'fields' : ('name', 'description'),
            }),
        (_('Conditions'), {
            'fields' : ('minimum_selected', 'maximum_selected', 'maximum_attendees', 'freeze_time'),
            'classes' : ('collapse', ),
            }),
        (_('Package'), {
            'fields' : ('package_solution', 'package_price'),
            'classes' : ('collapse', ),
            }),
        (_('Other'), {
            'fields' : ('order', 'public_statistic', 'lock_selections_on_acceptance'),
            }),)

    inlines = [TranslationInline,]

    def queryset(self, request):
        qs = super(OptionGroupAdmin, self).queryset(request)
        return qs.filter(event=request.bound_object)

    def _init_navigation(self):
        super(OptionGroupAdmin, self)._init_navigation()

        self.object_menu.register(self.page_change, self.Meta.display_name)

    def get_urls(self):
        from django.conf.urls import patterns, include

        option_admin = OptionAdmin()
        option_admin.page_root.parent = self.page_change
        option_admin.module_menu = self.module_menu
        option_admin.sadmin_menu = self.object_menu

        self.object_menu.register(option_admin.page_root)

        urlpattern = super(OptionGroupAdmin, self).get_urls()

        urlpattern = patterns('',
            (r'^(?P<bind_bind_pk>.+)/options/', include(option_admin.urls)),
        ) + urlpattern

        return urlpattern

    def save_form(self, request, form, change):
        instance = form.save(commit=False)

        if not change:
            instance.event = request.bound_object

        return instance

