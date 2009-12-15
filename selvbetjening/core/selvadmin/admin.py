from django.contrib import admin
from django.shortcuts import render_to_response
from django.template import RequestContext

class AdminSite(admin.AdminSite):


    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        urlpatterns = super(AdminSite, self).get_urls()

        #urlpatterns += patterns('',
        #    url(r'^oldadmin/$',
        #        self.admin_view(self.oldadmin),
        #        name='oldadmin')
        #    )

        return urlpatterns

    class Menu:
        links = []

site = AdminSite()