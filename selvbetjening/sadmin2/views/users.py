
"""
    See events.py for rules regarding sadmin2 views
"""

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
from selvbetjening.sadmin2.views.reports import insecure_reports_age, insecure_reports_address


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


@sadmin_prerequisites
def users_reports_age(request):

    context = {
        'sadmin2_menu_main_active': 'users',
        'sadmin2_breadcrumbs_active': 'users_reports_age',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_users,
        'sadmin2_menu_tab_active': 'reports'
    }

    return insecure_reports_age(
        request,
        SUser.objects.all(),
        extra_context=context
    )


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

