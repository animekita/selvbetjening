from django import template
from django.conf import settings
from django.contrib.admin import StackedInline
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.helpers import AdminForm

from selvbetjening.core.selvadmin.admin import site

from shortcuts import get_or_create_profile
from models import UserProfile
from forms import RegistrationForm

class UserProfileInline(StackedInline):
    model = UserProfile
    extra = 1
    max_num = 1

class UserAdminExt(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'display_age')
    
    def display_age(self, user):
        user_profile = get_or_create_profile(user)
        age = user_profile.get_age()
        return age
    display_age.admin_order_field = 'userprofile__dateofbirth'
    display_age.short_description = _('Age')
    
    add_form = RegistrationForm
    
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
                    request.user.message_set.create(message=msg + ' ' + ugettext("You may edit it again below."))
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