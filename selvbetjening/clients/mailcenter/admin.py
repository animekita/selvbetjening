from django.contrib import admin
from django.conf.urls.defaults import *

from selvbetjening.core.selvadmin.admin import site

from models import Mail
import admin_views

class MailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'date_created', 'is_draft')
    search_fields = ('subject',)

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
            url(r'^(.+)/send/$',
                admin_views.send,
                name='%s_%s_send' % info),
            url(r'^(.+)/send-preview/$',
                admin_views.send_preview,
                name='%s_%s_send_preview' % info),
            url(r'^(.+)/preview/',
                admin_views.preview,
                name='%s_%s_preview' % info),
            )

        return urlpatterns + super(MailAdmin, self).get_urls()

site.register(Mail, MailAdmin)