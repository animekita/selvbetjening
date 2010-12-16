from datetime import date

from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from django.db.models import Min, Max
from django.contrib.admin import StackedInline
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from selvbetjening.core.members.shortcuts import get_or_create_profile
from selvbetjening.core.members.models import UserProfile, UserWebsite, UserCommunication, to_age

from selvbetjening.sadmin.base.sadmin import SModelAdmin, SAdminContext

from selvbetjening.sadmin.members import nav

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
        app_name = 'members'
        name = 'user'
        model = User

    list_display = ('username', 'first_name', 'last_name', 'email', 'display_age')
    search_fields = ('id', 'username', 'first_name', 'last_name', 'email')
    readonly_fields = ('last_login', 'date_joined')

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
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Groups'), {'fields': ('groups',)}),
    )

    add_fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
    )

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        urlpattern = super(UserAdmin, self).get_urls()

        urlpattern = patterns('',
            url(r'^statistics/',
                self._wrap_view(self.user_statistics),
                name='%s_%s_statistics' % self._url_info),
            ) + urlpattern

        return urlpattern

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['menu'] = nav.browse_members_menu.render()
        extra_context['title'] = _(u'Browse Members')
        return super(UserAdmin, self).changelist_view(request, extra_context)

    def add_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['menu'] = nav.browse_members_menu.render()
        extra_context['title'] = _(u'Create Member')
        return super(UserAdmin, self).add_view(request, extra_context=extra_context)

    def change_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        extra_context['menu'] = nav.member_menu.render(username=object_id)
        return super(UserAdmin, self).change_view(request, object_id, extra_context=extra_context)

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

        def diff_in_months(ref_date, date):
            return (date.year - ref_date.year) * 12 + (date.month - ref_date.month)

        max_in_months = diff_in_months(join_stats['min'], join_stats['max'])

        join_span = [0] * (max_in_months + 1)

        for user in users:
            join_month = diff_in_months(join_stats['min'], user.date_joined)

            join_span[join_month] += 1

        join_span_acc = []
        acc = 0
        for item in join_span:
            acc = acc + item
            join_span_acc.append(acc)

        labels = []
        for x in range(0, max_in_months + 1):
            new_month = (join_stats['min'].month + x) % 12

            if new_month == 0:
                new_month = 1

            month = date(year=join_stats['min'].year + (join_stats['min'].month + x) / 12,
                         month=new_month,
                         day=1)

            labels.append(month.strftime("%B %Y"))

        return {'join_labels': labels,
                'join_data1': join_span,
                'join_data2': join_span_acc}

    def user_statistics(self, request):
        join_data = self.user_join_chart()
        age_data = self.user_age_chart()

        if join_data is None and age_data is None:
            return render_to_response('sadmin/members/no_statistics.html',
                                      context_instance=SAdminContext(request))

        if join_data is None:
            join_data = {}

        if age_data is None:
            age_data = {}

        age_data.update(join_data)

        age_data['menu'] = nav.browse_members_menu.render()

        return render_to_response('sadmin/members/statistics.html',
                                  age_data,
                                  context_instance=SAdminContext(request))
