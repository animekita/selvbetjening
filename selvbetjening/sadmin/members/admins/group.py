from django.utils.translation import ugettext as _
from django.contrib.auth.models import Group, User

from selvbetjening.sadmin.base.sadmin import SModelAdmin, STabularInline

def _user_count(group):
    return group.user_set.all().count()
_user_count.short_description = _('User count')

class UserTabularAdmin(STabularInline):
    model = User.groups.through
    readonly_fields = ('user',)
    extra = 0

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
    list_display = ('name', _user_count)

    inlines = [UserTabularAdmin,]

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = _(u'Browse Groups')

        return super(GroupAdmin, self).changelist_view(request, extra_context)