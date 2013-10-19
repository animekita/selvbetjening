
"""
    See events.py for rules regarding sadmin2 views
"""

from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group
from django.db.models import Max, Min
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from selvbetjening.core.members.models import to_age, UserLocation
from selvbetjening.core.user.models import SUser

from selvbetjening.sadmin2 import graph
from selvbetjening.sadmin2.forms import UserForm, GroupForm
from selvbetjening.sadmin2.decorators import sadmin_prerequisites
from selvbetjening.sadmin2 import menu

from generic import search_view, generic_create_view


@sadmin_prerequisites
def users_list(request):

    queryset = SUser.objects.all()
    columns = ('username',)

    context = {
        'sadmin2_menu_main_active': 'users',
        'sadmin2_breadcrumbs_active': 'users',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_users,
        'sadmin2_menu_tab_active': 'users',
    }

    return search_view(request,
                       queryset,
                       'sadmin2/users/list.html',
                       'sadmin2/users/list_inner.html',
                       search_columns=columns,
                       context=context)


@sadmin_prerequisites
def users_create(request):

    if request.method == 'POST':
        form = UserForm(request.POST)

        if form.is_valid():
            user = form.save()
            messages.add_message(request, messages.SUCCESS, _('User created'))
            return HttpResponseRedirect(reverse('sadmin2:user', kwargs={'user_pk': user.pk}))

    else:
        form = UserForm()

    return render(request,
                  'sadmin2/generic/form.html',
                  {
                      'sadmin2_menu_main_active': 'users',
                      'sadmin2_breadcrumbs_active': 'users_create',
                      'sadmin2_menu_tab': menu.sadmin2_menu_tab_users,
                      'sadmin2_menu_tab_active': 'users_create',

                      'form': form
                  })


@sadmin_prerequisites
def users_groups_list(request):

    queryset = Group.objects.all()
    columns = ('name',)

    context = {
        'sadmin2_menu_main_active': 'users',
        'sadmin2_breadcrumbs_active': 'users_groups',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_users,
        'sadmin2_menu_tab_active': 'groups',
    }

    return search_view(request,
                       queryset,
                       'sadmin2/users/groups_list.html',
                       'sadmin2/users/groups_list_inner.html',
                       search_columns=columns,
                       context=context)


@sadmin_prerequisites
def users_groups_create(request):

    context = {
        'sadmin2_menu_main_active': 'users',
        'sadmin2_breadcrumbs_active': 'users_groups_create',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_users,
        'sadmin2_menu_tab_active': 'groups',
    }

    return generic_create_view(request,
                               GroupForm,
                               reverse('sadmin2:users_groups_list'),
                               message_success=_('Group created'),
                               context=context)

@sadmin_prerequisites
def users_group(request, group_pk):

    group = get_object_or_404(Group, pk=group_pk)

    context = {
        'sadmin2_menu_main_active': 'users',
        'sadmin2_breadcrumbs_active': 'users_group',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_users,
        'sadmin2_menu_tab_active': 'groups',

        'group': group
    }

    return generic_create_view(request,
                               GroupForm,
                               reverse('sadmin2:users_group', kwargs={'group_pk': group.pk}),
                               message_success=_('Group updated'),
                               context=context,
                               instance=group)


def user_age_chart(min_age=5, max_age=80):
    cur_year = date.today().year

    # The graph looks stupid if we allow ages 0 and 100 et al.
    # Enforce sane limitations, lets say min 5 and max 80 years of age

    usersprofiles = SUser.objects.select_related()\
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


def user_join_chart():
    users = SUser.objects.all()

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
        acc += item
        join_span_acc.append(acc)

    labels = graph.generate_month_axis(join_stats['min'], join_stats['max'])

    return {'join_labels': labels,
            'join_data1': join_span,
            'join_data2': join_span_acc}

@sadmin_prerequisites
def users_reports_age(request):

    join_data = user_join_chart()
    age_data = user_age_chart()

    if join_data is None:
        join_data = {}

    if age_data is None:
        age_data = {}

    context = {
        'sadmin2_menu_main_active': 'users',
        'sadmin2_breadcrumbs_active': 'users_reports_age',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_users,
        'sadmin2_menu_tab_active': 'reports'
    }

    context.update(age_data)
    context.update(join_data)

    return render(request,
                  'sadmin2/users/reports/age.html',
                  context)


@sadmin_prerequisites
def users_reports_address(request):

    locations = UserLocation.objects.exclude(lat=None, lng=None).exclude(expired=True).select_related()
    expired = UserLocation.objects.filter(expired=True).count()
    invalid = UserLocation.objects.filter(expired=False).count() - locations.count()

    map_key = getattr(settings, 'MAP_KEY', None)



    context = {
        'sadmin2_menu_main_active': 'users',
        'sadmin2_breadcrumbs_active': 'users_reports_address',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_users,
        'sadmin2_menu_tab_active': 'reports',

        'locations': locations,
        'expired': expired,
        'invalid': invalid,
        'map_key': map_key
    }

    return render(request,
                  'sadmin2/users/reports/address.html',
                  context)

