from django import template
from django.conf import settings
from django.contrib.admin import StackedInline, TabularInline
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.contrib.admin.helpers import AdminForm
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.utils.datastructures import SortedDict

from selvbetjening.core.selvadmin.admin import site, reverse_lazy
from selvbetjening.data.invoice.models import Invoice

from shortcuts import get_or_create_profile
from models import UserProfile, UserWebsite, UserCommunication
from forms import RegistrationForm

import admin_views

class UserProfileInline(StackedInline):
    model = UserProfile
    extra = 1
    max_num = 1

class UserWebsiteInline(TabularInline):
    model = UserWebsite
    extra = 0

class UserCommunicationInline(TabularInline):
    model = UserCommunication
    extra = 0

class UserAdminExt(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'display_age')

    search_fields = ('id', 'username', 'first_name', 'last_name', 'email')

    def display_age(self, user):
        user_profile = get_or_create_profile(user)
        age = user_profile.get_age()
        return age
    display_age.admin_order_field = 'userprofile__dateofbirth'
    display_age.short_description = _('Age')

    add_form = RegistrationForm

    inlines = [UserProfileInline, UserWebsiteInline, UserCommunicationInline]

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
                               url(r'^statistics/',
                                   self.admin_site.admin_view(admin_views.user_statistics),
                                   {'model_admin': self},
                                   name='%s_%s_statistics' % info),
                               url(r'^migrate/',
                                   self.admin_site.admin_view(admin_views.user_migration),
                                   {'model_admin': self, 'admin_site': self.admin_site},
                                   name='%s_%s_migration' % info),
                               )

        urlpatterns += super(UserAdminExt, self).get_urls()

        return urlpatterns

    def add_to_menu(self, links):
        children = SortedDict()

        links['UserAdminExt'] = (_('Users'), reverse_lazy('admin:auth_user_changelist'),
                                 children)

        children['UserAdminExtGroups'] = (_('Groups'), reverse_lazy('admin:auth_group_changelist'))
        children['UserAdminExtStats'] = (_('Statistics'), reverse_lazy('admin:auth_user_statistics'))
        children['UserAdminExtMigration'] = (_('Migration'), reverse_lazy('admin:auth_user_migration'))

        return links

    def remove_from_menu(self, links):
        del links['UserAdminExt']

        return links

    def add_view(self, request):
        # copy of the original add_view, remove this if possible but damm
        # it is hard to get the template and forms overwritten ^^

        if not self.has_change_permission(request):
            if self.has_add_permission(request) and settings.DEBUG:
                # Raise Http404 in debug mode so that the user gets a helpful
                # error message.
                raise Http404('Your user does not have the "Change user" permission. In order to add users, Django requires that your user account have both the "Add user" and "Change user" permissions set.')
            raise PermissionDenied
        if request.method == 'POST':
            form = self.add_form(request.POST)
            if form.is_valid():
                new_user = form.save()
                msg = _('The %(name)s "%(obj)s" was added successfully.') % {'name': 'user', 'obj': new_user}
                self.log_addition(request, new_user)
                if "_addanother" in request.POST:
                    request.user.message_set.create(message=msg)
                    return HttpResponseRedirect(request.path)
                elif '_popup' in request.REQUEST:
                    return self.response_add(request, new_user)
                else:
                    request.user.message_set.create(message=msg + ' ' + _("You may edit it again below."))
                    return HttpResponseRedirect('../%s/' % new_user.id)
        else:
            form = self.add_form()

        adminform = AdminForm(form,
                          [(None, {'fields': form.base_fields.keys()})],
                          {}
                          )

        return render_to_response('admin/auth/user/add_user.html', {
            'title': _('Add user'),
            'form': form,
            'adminform' : adminform,
            'is_popup': '_popup' in request.REQUEST,
            'add': True,
            'change': False,
            'has_add_permission': True,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_file_field': False,
            'has_absolute_url': False,
            'auto_populated_fields': (),
            'opts': self.model._meta,
            'save_as': False,
            'username_help_text': self.model._meta.get_field('username').help_text,
            'root_path': self.admin_site.root_path,
            'app_label': self.model._meta.app_label,
        }, context_instance=template.RequestContext(request))

site.register(User, UserAdminExt)

from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group

site.register(Group, GroupAdmin)
