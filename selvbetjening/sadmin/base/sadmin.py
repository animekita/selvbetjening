from django.conf.urls.defaults import patterns, url, include
from django.template import RequestContext
from django.contrib import admin
from django.shortcuts import render_to_response
from django.views.decorators.cache import never_cache
from django.contrib.auth import logout as do_logout
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import views as auth_views
from selvbetjening.portal.profile.forms import LoginForm
from django.utils.functional import update_wrapper
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import get_object_or_404

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
                wrap(self.login),
                name='login'),
            url(r'^password_change/$',
                wrap(self.password_change, cacheable=True),
                name='password_change'),
            url(r'^password_change/done/$',
                wrap(self.password_change_done, cacheable=True),
                name='password_change_done'),
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
    add_form_template = None
    change_form_template = 'sadmin/base/change_form.html'
    change_list_template = 'sadmin/base/change_list.html'
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

            return view(request, *args, extra_context=extra_context, **kwargs)

        return self._wrap_view(update_wrapper(wrapper, view))

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        default_views = getattr(self.Meta, 'default_views',
                                ('list', 'add', 'delete', 'change'))

        urlpatterns = patterns('')

        if 'list' in default_views:
            urlpatterns += patterns('',
                url(r'^$',
                self._wrap_oldadmin_view(self.changelist_view),
                name='%s_%s_changelist' % self._url_info)
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

class SBoundModelAdmin(SModelAdmin):

    def _wrap_view(self, view):
        def wrapper(request, *args, **kwargs):
            bind_pk = kwargs.pop(getattr(self.Meta, 'bind_key', 'bind_pk'))
            bound_object = get_object_or_404(self.Meta.bound_model, pk=bind_pk)

            wrapped_request = ObjectWrapper(request)
            wrapped_request.bound_object = bound_object

            return view(wrapped_request, *args, **kwargs)

        return super(SBoundModelAdmin, self)._wrap_view(update_wrapper(wrapper, view))





