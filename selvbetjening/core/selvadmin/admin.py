from django.contrib import admin
from django.db.models.base import ModelBase
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.datastructures import SortedDict
from django.core.urlresolvers import reverse
from django.utils.functional import lazy

reverse_lazy = lazy(reverse, str)

class AdminSite(admin.AdminSite):
    def __init__(self, *args, **kwargs):
        self._extra_urlpatterns = []

        super(AdminSite, self).__init__(*args, **kwargs)

        self.Menu.links['AdminSite'] = ('Dashboard', reverse_lazy('admin:index'), ())

    def prepend_urlpattern(self, urlpattern):
        self._extra_urlpatterns = urlpattern + self._extra_urlpatterns

    def get_urls(self):
        return self._extra_urlpatterns + super(AdminSite, self).get_urls()

    def register(self, model, admin_class=None, **options):
        result = super(AdminSite, self).register(model, admin_class, **options)

        admin = self._registry[model]
        if hasattr(admin, 'add_to_menu'):
            admin.add_to_menu(self.Menu.links)

        return result

    def unregister(self, model):
        admin = self._registry[model]
        if hasattr(admin, 'remove_from_menu'):
            admin.remove_from_menu(self.Menu.links)

        return super(AdminSite, self).unregister(model)

    class Menu:
        """
        Structure
        [(name, url, [(name, url), ...], ...]

        The links array are manipulated by each ModelAdmin on register or
        unregister. Their add_to_menu and remove_from_menu function are called
        (if present) with the links array as an argument. It is the responsibility
        of the ModelAdmins to modify this list correctly.
        """
        links = SortedDict()

site = AdminSite()

# mailer
from mailer import admin as maileradmin

site.register(maileradmin.Message, maileradmin.MessageAdmin)
site.register(maileradmin.DontSendEntry, maileradmin.DontSendEntryAdmin)
site.register(maileradmin.MessageLog, maileradmin.MessageLogAdmin)