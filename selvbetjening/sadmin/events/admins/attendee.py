# -- encoding: utf-8 --
import operator

from django.utils.translation import ugettext as _
from django.contrib.admin.util import unquote
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.decorators import permission_required

from selvbetjening.core.events.models import Event, AttendState, Attend
from selvbetjening.core.events.models import Event, AttendState, Attend, AttendState
from selvbetjening.core.events.processor_handlers import change_selection_processors, checkin_processors
from selvbetjening.core.events.forms import PaymentForm, OptionForms
from selvbetjening.core.invoice.models import Invoice, Payment

from selvbetjening.sadmin.base.sadmin import SBoundModelAdmin, SAdminContext
from selvbetjening.sadmin.base.views import generic_search_page_unsecure
from selvbetjening.sadmin.base.sadmin import SAdminContext
from selvbetjening.sadmin.base.decorators import sadmin_access_required

from selvbetjening.sadmin.events import nav
from selvbetjening.sadmin.events.forms import CheckinForm, AttendeeForm
from selvbetjening.sadmin.events.admins.nonattendee import NonAttendeeAdmin
from selvbetjening.sadmin.events.admins.invoice import InvoiceAdmin

class AttendeeAdmin(SBoundModelAdmin):
    class Meta:
        app_name = 'events'
        name = 'attendee'
        model = Attend
        bound_model = Event
        default_views = ('list', 'delete', 'change')

    def in_balance(attend):
        return attend.invoice.in_balance()
    in_balance.boolean = True

    list_filter = ('state',)
    list_per_page = 50
    list_display = ('user', 'user_first_name', 'user_last_name', 'state', in_balance)

    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user', 'event', 'invoice')

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url, include

        urlpatterns = super(AttendeeAdmin, self).get_urls()

        urlpatterns = patterns('',
            url(r'^(.+)/selections/',
                self._wrap_view(self.selections_view),
                name='%s_%s_selections' % self._url_info),
            (r'^(?P<bind_invoice_pk>.+)/invoice/', include(InvoiceAdmin().urls)),
            (r'^new/', include(NonAttendeeAdmin().urls)),
            ) + urlpatterns

        return urlpatterns

    def queryset(self, request):
        qs = super(SBoundModelAdmin, self).queryset(request)

        return qs.filter(event=request.bound_object)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['menu'] = nav.event_menu.render(event_pk=request.bound_object.pk)

        return super(AttendeeAdmin, self).changelist_view(request, extra_context)

    def change_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        extra_context['menu'] = nav.attendee_menu.render(
            event_pk=request.bound_object.pk,
            attendee_pk=unquote(object_id))

        return super(AttendeeAdmin, self).change_view(request, object_id, extra_context)

    def selections_view(self, request, attendee_id):
        attendee = get_object_or_404(Attend, event=request.bound_object, pk=attendee_id)

        change_selection_handler = change_selection_processors.get_handler(request, attendee)

        if request.method == 'POST' and request.POST.get('submit_option', False):
            option_forms = OptionForms(attendee.event, request.POST, attendee=attendee)

            if change_selection_handler.is_valid() and option_forms.is_valid():
                change_selection_handler.save()
                option_forms.save()

                messages.success(request, _(u'Selections changed'))

        else:
            option_forms = OptionForms(attendee.event, attendee=attendee)

        checkin_parts = change_selection_handler.view()

        menu = nav.attendee_menu.render(event_pk=request.bound_object.pk,
                                        attendee_pk=attendee_id)

        return render_to_response('sadmin/events/attendee/selections.html',
                                  {'menu': menu,
                                   'attendee': attendee,
                                   'option_forms' : option_forms,
                                   'checkin_parts' : checkin_parts},
                                  context_instance=SAdminContext(request))

