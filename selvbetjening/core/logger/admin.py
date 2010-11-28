from django.contrib.admin import ModelAdmin
from django.contrib.admin.options import IncorrectLookupParameters
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from selvbetjening.core.selvadmin.admin import site

from models import Entry, SavedLog

class EntryAdmin(ModelAdmin):
    list_display = ('timestamp', 'module', 'category', 'message', 'ip', 'user', 'event')
    list_filter = ('event',)
    search_fields = ('module', 'category', 'message',
                     'ip', 'user__username', 'event__title')

    raw_id_fields = ('user', 'event')

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
                               url(r'^rss/show/([a-z0-9]+)/',
                                   self.rss_view,
                                   name='%s_%s_rss' % info),
                               url(r'^rss/manage/',
                                   self.admin_site.admin_view(self.rss_manage),
                                   name='%s_%s_manage_rss' % info),)

        urlpatterns += super(EntryAdmin, self).get_urls()

        return urlpatterns

    def rss_manage(self, request,
                   template_name='logger/admin/rss_manage.html'):

        get = ['::'.join([key, request.GET[key]]) for key in request.GET]
        serialized = '--'.join(get)

        import random
        import datetime
        import hashlib

        key_unhashed = str(datetime.datetime.now().microsecond) + '-' +\
                     str(random.randint(0, 2^64))

        key = hashlib.md5(key_unhashed).hexdigest()

        savedlog = SavedLog.objects.create(key=key, query=serialized)

        return render_to_response(template_name,
                                  {'savedlog' : savedlog},
                                  context_instance=RequestContext(request))


    def rss_view(self, request, key,
                 template_name='logger/admin/rss.html'):
        from django.contrib.admin.views.main import ERROR_FLAG

        savedlog = get_object_or_404(SavedLog, key=key)

        keyvalues = [keyvalue.split('::') for keyvalue in savedlog.query.split('--')]

        if (keyvalues[0][0] == ''):
            request.GET = {}
        else:
            request.GET = dict(keyvalues)

        ChangeList = self.get_changelist(request)
        try:
            cl = ChangeList(request, self.model, self.list_display,
                            self.list_display_links, self.list_filter,
                            self.date_hierarchy, self.search_fields,
                            self.list_select_related, self.list_per_page,
                            self.list_editable, self)
        except IncorrectLookupParameters:
            if ERROR_FLAG in request.GET.keys():
                return render_to_response(
                    'admin/invalid_setup.html', {'title': _('Database error')})

            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')

        cl.get_results(request)

        return render_to_response(template_name,
                                  {'cl' : cl,
                                   'savedlog' : savedlog},
                                  context_instance=RequestContext(request))

site.register(Entry, EntryAdmin)

class SavedLogAdmin(ModelAdmin):
    list_display = ('timestamp', 'key', 'query')

site.register(SavedLog, SavedLogAdmin)