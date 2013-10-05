from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from core.members.models import UserProfile
from sadmin2 import menu
from sadmin2.forms import UserForm, PasswordForm

from selvbetjening.sadmin2.views.generic import generic_create_view


def user_change(request, user_pk):

    user = get_object_or_404(UserProfile, pk=user_pk)

    context = {
        'sadmin2_menu_main_active': 'users',
        'sadmin2_breadcrumbs_active': 'user',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_user,
        'sadmin2_menu_tab_active': 'user',

        'user': user
    }

    return generic_create_view(request,
                               UserForm,
                               reverse('sadmin2:user', kwargs={'user_pk': user.pk}),
                               message_success=_('User updated'),
                               context=context,
                               instance=user)


def user_password(request, user_pk):

    user = get_object_or_404(UserProfile, pk=user_pk)

    context = {
        'sadmin2_menu_main_active': 'users',
        'sadmin2_breadcrumbs_active': 'user_password',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_user,
        'sadmin2_menu_tab_active': 'password',

        'user': user
    }

    return generic_create_view(request,
                               PasswordForm,
                               reverse('sadmin2:user_password', kwargs={'user_pk': user.pk}),
                               message_success=_('Password updated'),
                               context=context,
                               instance=user)