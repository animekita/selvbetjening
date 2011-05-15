from django.utils.translation import ugettext as _

from selvbetjening.core.events.models import Group

from selvbetjening.sadmin.base.sadmin import SModelAdmin

class GroupAdmin(SModelAdmin):
    class Meta:
        app_name = 'events'
        name = 'group'
        model = Group
        bound_model = Group
        display_name = _(u'Group')
        display_name_plural = _(u'Groups')

    list_display = ('name',)
