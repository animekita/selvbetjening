
"""
    See events.py for rules regarding sadmin2 views
"""
import datetime

from django.conf import settings
from django.contrib.auth.models import Group
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404

from selvbetjening.core.members.models import UserLocation
from selvbetjening.core.user.models import SUser

from selvbetjening.sadmin2.forms import UserForm, GroupForm
from selvbetjening.sadmin2.decorators import sadmin_prerequisites
from selvbetjening.sadmin2 import menu

from generic import search_view, generic_create_view
from selvbetjening.sadmin2.graphs.timelines import AgeTimeGraph, AbsoluteTimeGraph
from selvbetjening.sadmin2.graphs.units import UserAgeUnit, UserUnit
from selvbetjening.sadmin2.views.reports import insecure_reports_address


@sadmin_prerequisites
def users_list(request):

    queryset = SUser.objects.all()
    columns = ('pk', 'username', 'first_name', 'last_name', 'email')

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
                       search_order='-pk',
                       context=context)


@sadmin_prerequisites
def users_create(request):

    context = {
        'sadmin2_menu_main_active': 'users',
        'sadmin2_breadcrumbs_active': 'users_create',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_users,
        'sadmin2_menu_tab_active': 'users'
    }

    return generic_create_view(
        request,
        UserForm,
        redirect_success_url_callback=lambda instance: reverse('sadmin2:user', kwargs={'user_pk': instance.pk}),
        message_success=_('User created'),
        context=context,
        template='sadmin2/generic/form.html'
    )


@sadmin_prerequisites
def users_reports_users(request):

    graph = AbsoluteTimeGraph(AbsoluteTimeGraph.SCOPE.month,
                              UserUnit('Users'))

    return render(request, 'sadmin2/graphs/linegraph.html', {
        'sadmin2_menu_main_active': 'users',
        'sadmin2_breadcrumbs_active': 'users_reports_users',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_users,
        'sadmin2_menu_tab_active': 'reports',
        'title': _('Users'),
        'graph': graph
    })


@sadmin_prerequisites
def users_reports_age(request):

    graph = AgeTimeGraph(AbsoluteTimeGraph.SCOPE.year,
                         UserAgeUnit('Users'),
                         today=datetime.datetime.today())

    return render(request, 'sadmin2/graphs/linegraph.html', {
        'sadmin2_menu_main_active': 'users',
        'sadmin2_breadcrumbs_active': 'users_reports_age',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_users,
        'sadmin2_menu_tab_active': 'reports',
        'title': _('User age'),
        'graph': graph
    })


@sadmin_prerequisites
def users_reports_address(request):

    context = {
        'sadmin2_menu_main_active': 'users',
        'sadmin2_breadcrumbs_active': 'users_reports_address',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_users,
        'sadmin2_menu_tab_active': 'reports'
    }

    return insecure_reports_address(
        request,
        UserLocation.objects.all(),
        extra_context=context
    )

