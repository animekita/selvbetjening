from datetime import date

from django.conf import settings
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Min, Max
from django.contrib.admin import StackedInline
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.utils.html import escape
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.defaults import RequestContext

from selvbetjening.core.members.shortcuts import get_or_create_profile
from selvbetjening.core.members.models import UserProfile, UserWebsite, UserCommunication, UserLocation, to_age

from selvbetjening.sadmin.base import graph
from selvbetjening.sadmin.base.sadmin import SModelAdmin, main_menu
from selvbetjening.sadmin.base.nav import SPage, LeafSPage

from selvbetjening.sadmin.members.admins.group import GroupAdmin
from selvbetjening.sadmin.members.admins.access import AccessAdmin


class UserProfileInline(StackedInline):
    model = UserProfile
    extra = 1
    max_num = 1
    can_delete = False


class UserWebsiteInline(StackedInline):
    model = UserWebsite
    extra = 0


class UserCommunicationInline(StackedInline):
    model = UserCommunication
    extra = 0


class UserAdmin(SModelAdmin):
    class Meta:
        app_name = 'auth'
        name = 'user'
        display_name_plural = _('Users')
        display_name = _('User')
        model = User

    list_display = ('username', 'first_name', 'last_name', 'display_age')
    search_fields = ('id', 'username', 'first_name', 'last_name', 'email')
    readonly_fields = ('last_login', 'date_joined')
    list_filter = ['is_superuser', 'is_staff', 'is_active']

    inlines = [UserProfileInline, UserWebsiteInline, UserCommunicationInline]

    def display_age(self, user):
        user_profile = get_or_create_profile(user)
        age = user_profile.get_age()
        return age
    display_age.admin_order_field = 'userprofile__dateofbirth'
    display_age.short_description = _('Age')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Important dates'), {'fields': (('last_login', 'date_joined'),)}),
    )

    add_fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
    )

    def _init_navigation(self):
        super(UserAdmin, self)._init_navigation()

        main_menu.register(self.page_root)

        self.page_statistics = SPage(_('Statistics'),
                                     'sadmin:%s_%s_statistics' % self._url_info,
                                     parent=self.page_root,
                                     permission=lambda user: user.has_perm('%s.change_%s' % self._url_info))

        self.page_map = SPage(_('Map'),
                              'sadmin:%s_%s_map' % self._url_info,
                              parent=self.page_root,
                              permission=lambda user: user.has_perm('%s.change_%s' % self._url_info))

        self.page_change_password = LeafSPage(_('Change Password'),
                                              'sadmin:%s_%s_change_password' % self._url_info,
                                              parent=self.page_change,
                                              permission=lambda user: user.has_perm('%s.change_%s' % self._url_info))

        self.module_menu.register(self.page_statistics)
        self.module_menu.register(self.page_map)

        self.object_menu.register(self.page_change, title=_(u'User'))
        self.object_menu.register(self.page_change_password)

    def get_urls(self):
        from django.conf.urls import patterns, url, include

        urlpattern = super(UserAdmin, self).get_urls()

        group_admin = GroupAdmin()
        group_admin.page_root.parent = self.page_root
        group_admin.module_menu = self.module_menu
        self.module_menu.register(group_admin.page_root)

        access_admin = AccessAdmin()
        access_admin.page_change.parent = self.page_change
        access_admin.module_menu = self.module_menu
        access_admin.object_action_menu = self.object_action_menu
        access_admin.object_menu = self.object_menu
        self.object_menu.register(access_admin.page_change, title=_(u'Access'))

        urlpattern = patterns('',
            url(r'^statistics/',
                self._wrap_view(self.user_statistics),
                name='%s_%s_statistics' % self._url_info),
            url(r'^map/',
                self._wrap_view(self.map_view),
                name='%s_%s_map' % self._url_info),
            url(r'^(\d+)/password/$',
                self._wrap_view(self.user_change_password),
                name='%s_%s_change_password' % self._url_info),
            (r'^', include(access_admin.urls)),
            (r'^groups/', include(group_admin.urls)),
            ) + urlpattern

        return urlpattern

    def queryset(self, request):
        qs = super(UserAdmin, self).queryset(request)
        return qs.prefetch_related('userprofile_set')  # improves performance for age column

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = _(u'Browse Members')
        return super(UserAdmin, self).changelist_view(request, extra_context)

    def add_view(self, request, extra_context=None, **kwargs):
        extra_context = extra_context or {}
        extra_context['title'] = _(u'Create Member')

        # fix problem with creating users with profiles directly
        inlines_old = self.inlines
        self.inlines = []
        # fix end

        result = super(UserAdmin, self).add_view(request, extra_context=extra_context, **kwargs)

        # restore from fix
        self.inlines = inlines_old

        return result

    def user_change_password(self, request, username):
        """
        This function have been lifted from the real UserAdmin
        class, with slight modifications.
        """
        user = get_object_or_404(User, pk=username)
        if request.method == 'POST':
            form = AdminPasswordChangeForm(user, request.POST)
            if form.is_valid():
                form.save()
                msg = _('Password changed successfully.')
                messages.success(request, msg)
                return HttpResponseRedirect('..')
        else:
            form = AdminPasswordChangeForm(user)

        fieldsets = [(None, {'fields': form.base_fields.keys()})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        return render_to_response('admin/auth/user/change_password.html', {
            'title': _('Change password: %s') % escape(user.username),
            'adminForm': adminForm,
            'form_url': '',
            'form': form,
            'is_popup': '_popup' in request.REQUEST,
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
            'menu': self.module_menu,
            'object_menu': self.object_menu,
            'action_menu': self.object_action_menu,
            'current_page': self.page_change_password,
        }, context_instance=RequestContext(request))

    def user_age_chart(self, min_age=5, max_age=80):
        cur_year = date.today().year

        # The graph looks stupid if we allow ages 0 and 100 et al.
        # Enforce sane limitations, lets say min 5 and max 80 years of age

        usersprofiles = UserProfile.objects.select_related()\
                                           .filter(dateofbirth__lt=date(cur_year-min_age, 1, 1))\
                                           .filter(dateofbirth__gt=date(cur_year-max_age, 1, 1))

        if usersprofiles.count() == 0:
            return None

        age_stats = usersprofiles.aggregate(min=Max('dateofbirth'),
                                            max=Min('dateofbirth'))

        age_stats['max'], age_stats['min'] = (to_age(age_stats['max']),
                                              to_age(age_stats['min']))

        age_span = [0] * (age_stats['max'] - age_stats['min'] + 1)

        sum = count = 0
        for usersprofile in usersprofiles:
            age = usersprofile.get_age()

            age_span[age - age_stats['min']] += 1
            sum += age
            count += 1

        return {'age_labels': range(age_stats['min'], age_stats['max'] + 1),
                'age_data': age_span,
                'min': age_stats['min'],
                'max': age_stats['max'],
                'avg': float(sum)/float(count),
                'max_limit': max_age,
                'min_limit': min_age}

    def user_join_chart(self):
        users = User.objects.all()

        if users.count() == 0:
            return None

        join_stats = users.aggregate(max=Max('date_joined'),
                                     min=Min('date_joined'))

        max_in_months = graph.diff_in_months(join_stats['min'], join_stats['max'])

        join_span = [0] * (max_in_months + 1)

        for user in users:
            join_month = graph.diff_in_months(join_stats['min'], user.date_joined)

            join_span[join_month] += 1

        join_span_acc = []
        acc = 0
        for item in join_span:
            acc = acc + item
            join_span_acc.append(acc)

        labels = graph.generate_month_axis(join_stats['min'], join_stats['max'])

        return {'join_labels': labels,
                'join_data1': join_span,
                'join_data2': join_span_acc}

    def user_statistics(self, request):
        join_data = self.user_join_chart()
        age_data = self.user_age_chart()

        if join_data is None:
            join_data = {}

        if age_data is None:
            age_data = {}

        age_data.update(join_data)

        age_data['menu'] = self.module_menu
        age_data['current_page'] = self.page_statistics

        return render_to_response('sadmin/members/statistics.html',
                                  age_data,
                                  context_instance=RequestContext(request))

    def map_view(self, request):

        locations = UserLocation.objects.exclude(lat=None, lng=None).exclude(expired=True).select_related()
        expired = UserLocation.objects.filter(expired=True).count()
        invalid = UserLocation.objects.filter(expired=False).count() - locations.count()

        map_key = getattr(settings, 'MAP_KEY', None)

        return render_to_response('sadmin/members/map.html',
                                  {'menu': self.module_menu,
                                   'current_page': self.page_map,
                                   'locations': locations,
                                   'expired': expired,
                                   'invalid': invalid,
                                   'map_key': map_key},
                                  context_instance=RequestContext(request))
