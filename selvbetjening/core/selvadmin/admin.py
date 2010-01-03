from django.contrib import admin
from django.shortcuts import render_to_response
from django.template import RequestContext

class AdminSite(admin.AdminSite):
    def __init__(self, *args, **kwargs):
        self._extra_urlpatterns = []

        super(AdminSite, self).__init__(*args, **kwargs)

    def prepend_urlpattern(self, urlpattern):
        self._extra_urlpatterns = urlpattern + self._extra_urlpatterns

    def get_urls(self):
        return self._extra_urlpatterns + super(AdminSite, self).get_urls()

    class Menu:
        links = []

site = AdminSite()