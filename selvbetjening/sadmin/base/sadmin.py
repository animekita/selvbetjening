from contextlib import contextmanager

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
from django.utils.safestring import mark_safe
from django.utils.datastructures import SortedDict
from django.core.urlresolvers import NoReverseMatch

from selvbetjening.portal.profile.forms import LoginForm
from selvbetjening.core import ObjectWrapper

from navtree.navigation import Navigation

from nav import LeafSPage, ObjectSPage, SPage
from widgets import SAdminForeignKeyRawIdWidget, register_object_search_page

main_menu = Navigation() # default sadmin navigation

@contextmanager
def reverse_patch(request, smodel_admin):
    """
    Patch the reverse function for particular Django admin views

    The Django admin views (change, changelist, add, and delete)
    now (from 1.4) uses the reverse function to redirect users
    after specific actions (such as deleting an object).
    Unfortunately, this clashes with SAdmin, since additional
    args must be provided in order to reverse bound admin
    models.

    We can't overwrite the usage of reverse by defining new
    methods on SModelAdmin (we can, but it will overwrite
    large quantities of logic). So we patch the reverse
    function when rendering each view.

    This should be sound, since Django is executed in a single
    process. We take great care in restoring the real reverse
    function again after the view has rendered, e.g. we
    implement this using the new "with" statement in Python.
    """

    import django.contrib.admin.options as admin_impl
    old_reverse = admin_impl.reverse

    def reverse_injected(*args, **kwargs):
        try:
            return old_reverse(*args, **kwargs)
        except NoReverseMatch:
            url_args = [obj.pk for obj in smodel_admin._get_navigation_stack(request)]

            for arg in kwargs.get('args', []):
                url_args.append(arg)

            kwargs['args'] = url_args

            return old_reverse(*args, **kwargs)

    try:
        admin_impl.reverse = reverse_injected
        yield

    finally:
        admin_impl.reverse = old_reverse

class SAdminSite(admin.AdminSite):
    def __init__(self):
        super(SAdminSite, self).__init__()

        self.app_name = 'admin'
        self.name = 'sadmin'

        self.page_root = SPage('Dashboard',
                               'sadmin:dashboard')
        
        self._registry = SortedDict()

    def register(self, mount, modeladmin):
        self._registry[mount] = modeladmin()
                    
        if self._registry[mount].page_root.parent is None:
            self._registry[mount].page_root.parent = self.page_root        

    def unregister(self, *args, **kwargs):
        raise NotImplementedError

    def get(self, mount):
        return self._registry[mount]

    def get_urls(self):
        """
        Modified version of get_urls from admin, removed
        unused views and added custom sadmin views
        """
        
        from django.conf.urls import patterns, url, include

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

        urlpatterns += patterns('',
            *[(r'^%s/' % mount, include(self._registry[mount].urls)) for mount in self._registry]
            )

        return urlpatterns

    @never_cache
    def index(self, request, extra_context=None):
        return render_to_response('sadmin/base/dashboard.html',
                                  context_instance=RequestContext(request))

    @never_cache
    def logout(self, request, extra_context=None):
        do_logout(request)

        messages.success(request, _(u'User successfully logged out'))

        return HttpResponseRedirect(reverse('sadmin:login'))

    @never_cache
    def login(self, request, extra_context=None):
        wrapped_request = ObjectWrapper(request)

        if request.REQUEST.get(REDIRECT_FIELD_NAME, None) is None:
            wrapped_request.REQUEST = request.GET.copy()
            wrapped_request.REQUEST[REDIRECT_FIELD_NAME] = reverse('sadmin:dashboard')

        return auth_views.login(wrapped_request,
                                template_name='sadmin/base/login.html',
                                authentication_form=LoginForm,
                                extra_context=extra_context)

site = SAdminSite()

class SModelAdmin(admin.ModelAdmin):
    depth = 0

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

        # Django now uses the models internal opts (Options)
        # object for the module name (name in our Meta object).
        #
        # We inject the "correct" module name without overwriting
        # the value of the object (since the object is global).
        self.opts = ObjectWrapper(self.opts)
        self.opts.module_name = self.Meta.name

        self._init_navigation()

    def _init_navigation(self):
        """
        The navigation is divided into three menus

        module_menu: navigation for this top admin module

        sadmin_menu: navigation for "non-object" pages
        sadmin_action_menu: action navigation for "non-object" pages

        object_menu: navigation for a specific object or view
        object_action_menu: actions for an object
        object_related_menu: cross navigation to other admin views
        """

        default_views = getattr(self.Meta, 'default_views',
                                ('list', 'add', 'delete', 'change'))

        self.module_menu = Navigation()
        self.sadmin_menu = Navigation()
        self.sadmin_action_menu = Navigation()
        self.object_menu = Navigation()
        self.object_action_menu = Navigation()
        self.object_related_menu = Navigation()

        if 'list' in default_views:
            self.page_root = SPage(
                getattr(self.Meta, 'display_name_plural', self.Meta.name),
                'sadmin:%s_%s_changelist' % self._url_info,
                permission=lambda user: user.has_perm('%s.change_%s' % self._url_info),
                depth=self.depth)
            self.module_menu.register(self.page_root)

            register_object_search_page(self.Meta.app_name,
                                        self.Meta.name,
                                        'sadmin:%s_%s_changelist' % self._url_info)
        else:
            self.page_root = None

        if 'add' in default_views:
            self.page_add = SPage(
                _('Create'),
                'sadmin:%s_%s_add' % self._url_info,
                parent=self.page_root,
                permission=lambda user: user.has_perm('%s.add_%s' % self._url_info),
                depth=self.depth)
            self.sadmin_action_menu.register(self.page_add)

        if 'change' in default_views:
            self.page_change = ObjectSPage(
                'sadmin:%s_%s_change' % self._url_info,
                parent=self.page_root,
                permission=lambda user: user.has_perm('%s.change_%s' % self._url_info),
                depth=self.depth)

        if 'delete' in default_views:
            self.page_delete = LeafSPage(
                _('Delete'),
                'sadmin:%s_%s_delete' % self._url_info,
                parent=self.page_change,
                permission=lambda user: user.has_perm('%s.delete_%s' % self._url_info),
                depth=self.depth)
            self.object_action_menu.register(self.page_delete)

    def _get_navigation_stack(self, request):
        return []

    def _wrap_view(self, view):
        def wrapper(request, *args, **kwargs):
            return self.admin_site.admin_view(view)(request, *args, **kwargs)
        return update_wrapper(wrapper, view)

    def get_urls(self):
        from django.conf.urls import patterns, url

        default_views = getattr(self.Meta, 'default_views',
                                ('list', 'add', 'delete', 'change'))

        urlpatterns = patterns('')

        if 'list' in default_views:
            urlpatterns += patterns('',
                url(r'^$',
                    self._wrap_view(self.changelist_view),
                    name='%s_%s_changelist' % self._url_info),
                url(r'^ajax/search/$',
                    self._wrap_view(self.changelist_ajax_view),
                    name='%s_%s_changelist_ajax' % self._url_info)
                )

        if 'add' in default_views:
            urlpatterns += patterns('',
                url(r'^add/$',
                    self._wrap_view(self.add_view),
                    name='%s_%s_add' % self._url_info)
                )

        if 'delete' in default_views:
            urlpatterns += patterns('',
                url(r'^(.+)/delete/$',
                    self._wrap_view(self.delete_view),
                    name='%s_%s_delete' % self._url_info)
                )

        if 'change' in default_views:
            urlpatterns += patterns('',
                url(r'^(.+)/$',
                    self._wrap_view(self.change_view),
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

    def change_view(self, request, object_id, extra_context=None, **kwargs):
        context = {}
        
        context['menu'] = self.module_menu
        context['object_menu'] = self.object_menu
        context['action_menu'] = self.object_action_menu
        context['current_page'] = self.page_change
        context['object_related_menu'] = self.object_related_menu
        context['title'] = _('Change %s') % self.Meta.display_name
        
        context.update(extra_context or {})

        with reverse_patch(request, self):
            return super(SModelAdmin, self).change_view(request, object_id, extra_context=context, **kwargs)

    def add_view(self, request, extra_context=None, **kwargs):
        context = {}
        
        context['current_page'] = self.page_add
        context['menu'] = self.module_menu
        context['object_menu'] = self.sadmin_menu
        context['action_menu'] = self.sadmin_action_menu
        
        context.update(extra_context or {})

        with reverse_patch(request, self):
            return super(SModelAdmin, self).add_view(request, extra_context=context, **kwargs)

    def delete_view(self, request, object_id, extra_context=None):
        context = {}
        
        context['current_page'] = self.page_delete
        context['menu'] = self.module_menu
        context['object_menu'] = self.object_menu
        context['action_menu'] = self.object_action_menu
        context['title'] = _(u'Delete %s') % self.Meta.display_name

        context.update(extra_context or {})

        with reverse_patch(request, self):
            return super(SModelAdmin, self).delete_view(request, object_id, extra_context=context)

    def changelist_view(self, request, extra_context=None):
        args = [obj.pk for obj in self._get_navigation_stack(request)]
        search_url = reverse('sadmin:%s_%s_changelist_ajax' % \
                             self._url_info, args=args)

        extra_params = request.GET.copy()
        extra_params.pop('q', None)

        search_url = search_url + '?' + extra_params.urlencode()

        if len(extra_params) > 0:
            search_url = search_url + '&q='
        else:
            search_url = search_url + 'q='

        context = {}
        context['search_url'] = mark_safe(search_url)

        context['title'] = _(u'Browse %s') % self.Meta.display_name_plural

        context['current_page'] = self.page_root
        context['menu'] = self.module_menu
        context['action_menu'] = self.sadmin_action_menu
        context['object_menu'] = self.sadmin_menu
        
        context.update(extra_context or {})

        with reverse_patch(request, self):
            return super(SModelAdmin, self).changelist_view(request, extra_context=context)

    def changelist_ajax_view(self, request, extra_context=None):
        response = self.changelist_view(request, extra_context)

        response.render()
        start = response.content.rfind('<form')
        stop = response.content.rfind('</form>') + 7
        response.content = response.content[start:stop]

        return response

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """ Overwrites the standard ForeignKeyRawIdWidget for all raw id fields """

        db = kwargs.get('using')
        if db_field.name in self.raw_id_fields:
            kwargs['widget'] = SAdminForeignKeyRawIdWidget(db_field.rel, self.admin_site, using=db)

            return db_field.formfield(**kwargs)

        return super(SModelAdmin, self).formfield_for_foreignkey(db_field, request=request, **kwargs)


class SBoundModelAdmin(SModelAdmin):
    depth = 1

    def _wrap_view(self, view):
        def wrapper(request, *args, **kwargs):
            bind_pk = kwargs.pop(getattr(self.Meta, 'bind_key', 'bind_pk'))
            bound_object = get_object_or_404(self.Meta.bound_model, pk=bind_pk)

            wrapped_request = ObjectWrapper(request)
            wrapped_request.bound_object = bound_object

            extra_context = kwargs.get('extra_context', {})
            extra_context['navigation_stack'] = self._get_navigation_stack(wrapped_request)
            kwargs['extra_context'] = extra_context

            return view(wrapped_request, *args, **kwargs)

        wrapped_view = update_wrapper(wrapper, view)
        return super(SBoundModelAdmin, self)._wrap_view(wrapped_view)

    def _get_navigation_stack(self, request):
        return [request.bound_object,]

class STabularInline(admin.TabularInline):
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """ Overwrites the standard ForeignKeyRawIdWidget for all raw id fields """

        db = kwargs.get('using')
        if db_field.name in self.raw_id_fields:
            kwargs['widget'] = SAdminForeignKeyRawIdWidget(db_field.rel, self.admin_site, using=db)

            return db_field.formfield(**kwargs)

        return super(STabularInline, self).formfield_for_foreignkey(db_field, request=request, **kwargs)


