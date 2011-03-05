from django.utils.translation import ugettext as _
from django.contrib.auth.models import Group

from selvbetjening.sadmin.base.sadmin import SModelAdmin

class GroupAdmin(SModelAdmin):
    class Meta:
        app_name = 'members'
        name = 'group'
        display_name_plural = _('Groups')
        display_name = _('Group')
        model = Group

    search_fields = ('name',)
    ordering = ('name',)
    filter_horizontal = ('permissions',)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = _(u'Browse Groups')

        return super(GroupAdmin, self).changelist_view(request, extra_context)