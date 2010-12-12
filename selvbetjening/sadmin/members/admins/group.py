from django.utils.translation import ugettext as _
from django.db.models import Count
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group

from selvbetjening.core.translation.admin import TranslationInline
from selvbetjening.core.events.models import Event, AttendState
from selvbetjening.core.events.models import Event, AttendState, Attend, AttendState
from selvbetjening.core.events.processor_handlers import change_selection_processors, checkin_processors
from selvbetjening.core.events.forms import PaymentForm, OptionForms
from selvbetjening.core.invoice.models import Invoice, Payment
from selvbetjening.core.members.shortcuts import get_or_create_profile

from selvbetjening.sadmin.base.sadmin import SModelAdmin
from selvbetjening.sadmin.base.views import generic_search_page_unsecure
from selvbetjening.sadmin.base.sadmin import SAdminContext
from selvbetjening.sadmin.base.decorators import sadmin_access_required

from selvbetjening.sadmin.members import nav

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
from selvbetjening.core.invoice.models import Invoice

from selvbetjening.core.members.models import UserProfile, UserWebsite, UserCommunication

import operator

class GroupAdmin(SModelAdmin):
    class Meta:
        app_name = 'members'
        name = 'group'
        model = Group

    search_fields = ('name',)
    ordering = ('name',)
    filter_horizontal = ('permissions',)