from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from selvbetjening.sadmin.base.sadmin import SModelAdmin
from selvbetjening.sadmin.base.nav import LeafSPage

class AccessAdmin(SModelAdmin):
    class Meta:
        app_name = 'auth'
        name = 'access'
        display_name = _('Access')
        model = User
        default_views = ('change',)

    fieldsets = (
        (_('Groups'), {'fields': ('groups',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
    )

    def _init_navigation(self):
        super(AccessAdmin, self)._init_navigation()

        self.page_change = LeafSPage(
            self.Meta.display_name,
            'sadmin:%s_%s_change' % self._url_info,
            parent=self.page_root,
            permission=lambda user: user.has_perm('%s.change_%s' % self._url_info),
            depth=self.depth)

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        urlpatterns = patterns('',
                               url(r'^(\d+)/access/$',
                                   self._wrap_view(self.change_view),
                                   name='%s_%s_change' % self._url_info)
                               )

        return urlpatterns

