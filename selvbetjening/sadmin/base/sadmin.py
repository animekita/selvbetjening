from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.cache import never_cache
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.functional import update_wrapper
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.contrib.auth import logout as do_logout
from django.contrib import messages
from django.template import mark_safe

from selvbetjening.portal.profile.forms import LoginForm
from selvbetjening.core import ObjectWrapper

import nav

class SAdminContext(RequestContext):
    """
    Global context manipulation for all SAdmin views.

    All SAdmin views should use this context, or include the
    dictionary created by the static process method.
    """

    def __init__(self, request, dict=None, *args, **kwargs):
        dict = SAdminContext.process(request, dict)
        super(SAdminContext, self).__init__(request, dict, *args, **kwargs)

    @staticmethod
    def process(request, dict=None):
        dict = dict or {}
        dict['main_menu'] = nav.registry['main'].render()

        return dict

class SAdminSite(admin.AdminSite):
    def __init__(self):
        super(SAdminSite, self).__init__()

        self.app_name = 'sadmin'
        self.name = 'sadmin'

    def register(self, mount, modeladmin):
        self._registry[mount] = modeladmin()

    def unregister(self, *args, **kwargs):
        raise NotImplemented

    def get_urls(self):
        """
        Modified version of get_urls from admin, removed
        unused views and added custom sadmin views
        """
        from django.conf.urls.defaults import patterns, url, include

        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        urlpatterns = patterns('',
            url(r'^$',
                wrap(self.index),
                name='dashboard'),
            url(r'^logout/$',
                wrap(self.logout),
                name='logout'),
            url(r'^login/$',
                self.login,
                name='login'),
            url(r'^jsi18n/$',
                wrap(self.i18n_javascript, cacheable=True),
                name='jsi18n'),
        )

        urlpatterns += patterns('selvbetjening.sadmin.base.views',
            *[(r'^%s/' % mount, include(self._registry[mount].urls)) for mount in self._registry]
            )

        return urlpatterns

    @never_cache
    def index(self, request, extra_context=None):
        return render_to_response('sadmin/base/dashboard.html',
                                  context_instance=SAdminContext(request))

    @never_cache
    def logout(self, request):
        do_logout(request)

        messages.success(request, _(u'User sucessfully logged out'))

        return HttpResponseRedirect(reverse('sadmin:login'))

    @never_cache
    def login(self, request):
        wrapped_request = ObjectWrapper(request)

        if request.REQUEST.get(REDIRECT_FIELD_NAME, None) is None:
            wrapped_request.REQUEST = request.GET.copy()
            wrapped_request.REQUEST[REDIRECT_FIELD_NAME] = reverse('sadmin:dashboard')

        return auth_views.login(wrapped_request,
                                template_name='sadmin/base/login.html',
                                authentication_form=LoginForm)

site = SAdminSite()

class SModelAdmin(admin.ModelAdmin):
    add_form_template = 'sadmin/base/add_form.html'
    change_form_template = 'sadmin/base/change_form.html'
    change_list_template = 'sadmin/base/change_list.html'
    change_list_ajax_template = 'sadmin/base/change_list_ajax.html'
    delete_confirmation_template = None
    delete_selected_confirmation_template = None
    object_history_template = None

    def __init__(self):
        super(SModelAdmin, self).__init__(self.Meta.model, site)
        self._url_info = self.Meta.app_name, self.Meta.name

    def _wrap_view(self, view):
        def wrapper(request, *args, **kwargs):
            return self.admin_site.admin_view(view)(request, *args, **kwargs)
        return update_wrapper(wrapper, view)

    def _wrap_oldadmin_view(self, view):
        def wrapper(request, *args, **kwargs):
            extra_context = kwargs.pop('extra_context', {})
            extra_context = SAdminContext.process(extra_context)
            kwargs['extra_context'] = extra_context

            return view(request, *args, **kwargs)

        return self._wrap_view(update_wrapper(wrapper, view))

    def _get_extra_url_args(self, request):
        return []

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        default_views = getattr(self.Meta, 'default_views',
                                ('list', 'add', 'delete', 'change'))

        urlpatterns = patterns('')

        if 'list' in default_views:
            urlpatterns += patterns('',
                url(r'^$',
                    self._wrap_oldadmin_view(self.changelist_view),
                    name='%s_%s_changelist' % self._url_info),
                url(r'^ajax/search/$',
                    self._wrap_oldadmin_view(self.changelist_ajax_view),
                    name='%s_%s_changelist_ajax' % self._url_info)
                )

        if 'add' in default_views:
            urlpatterns += patterns('',
                url(r'^add/$',
                    self._wrap_oldadmin_view(self.add_view),
                    name='%s_%s_add' % self._url_info)
                )

        if 'delete' in default_views:
            urlpatterns += patterns('',
                url(r'^(.+)/delete/$',
                    self._wrap_oldadmin_view(self.delete_view),
                    name='%s_%s_delete' % self._url_info)
                )

        if 'change' in default_views:
            urlpatterns += patterns('',
                url(r'^(.+)/$',
                    self._wrap_oldadmin_view(self.change_view),
                    name='%s_%s_change' % self._url_info)
                )

        return urlpatterns

    def get_fieldsets(self, request, obj=None):
        """
        Adds add_fieldsets as an alternative to the normal fieldsets for the add form
        """
        if obj is None and hasattr(self, 'add_fieldsets'):
            return self.add_fieldsets
        else:
            return super(SModelAdmin, self).get_fieldsets(request, obj)

    def changelist_view(self, request, extra_context):

        search_url = reverse('sadmin:%s_%s_changelist_ajax' % \
                             self._url_info, args=self._get_extra_url_args(request))

        extra_params = request.GET.copy()
        extra_params.pop('q', None)

        search_url = search_url + '?' + extra_params.urlencode()

        if len(extra_params) > 0:
            search_url = search_url + '&q='
        else:
            search_url = search_url + 'q='

        extra_context = extra_context or {}
        extra_context['search_url'] = mark_safe(search_url)

        return super(SModelAdmin, self).changelist_view(request, extra_context)

    def changelist_ajax_view(self, request, extra_context=None):
        response = self.changelist_view(request, extra_context)

        start = response.content.rfind('<form')
        stop = response.content.rfind('</form>') + 7
        response.content = response.content[start:stop]

        return response

class SBoundModelAdmin(SModelAdmin):

    def _wrap_view(self, view):
        def wrapper(request, *args, **kwargs):
            bind_pk = kwargs.pop(getattr(self.Meta, 'bind_key', 'bind_pk'))
            bound_object = get_object_or_404(self.Meta.bound_model, pk=bind_pk)

            wrapped_request = ObjectWrapper(request)
            wrapped_request.bound_object = bound_object

            return view(wrapped_request, *args, **kwargs)

        return super(SBoundModelAdmin, self)._wrap_view(update_wrapper(wrapper, view))

    def _get_extra_url_args(self, request):
        return [request.bound_object.pk,]



