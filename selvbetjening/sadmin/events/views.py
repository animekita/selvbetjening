import operator

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.decorators import permission_required

from selvbetjening.core.events.models import Event, AttendState, Attend, AttendState
from selvbetjening.core.events.processor_handlers import change_selection_processors, checkin_processors
from selvbetjening.core.events.forms import PaymentForm, OptionForms
from selvbetjening.core.invoice.models import Invoice, Payment

from selvbetjening.sadmin.base.views import generic_search_page_unsecure
from selvbetjening.sadmin.base.sadmin import SAdminContext
from selvbetjening.sadmin.base.decorators import sadmin_access_required

from forms import CheckinForm, AttendeeForm



#@sadmin_access_required
#@permission_required('events.change_event')
#def view_attendees(request,
                   #event_id,
                   #template_name='sadmin/events/event/attendees.html'):

    #event = get_object_or_404(Event, pk=event_id)

    #search_fields = ('user__first_name', 'user__last_name', 'user__username')

    #return generic_search_page_unsecure(request,
                                        #search_fields=search_fields,
                                        #queryset=event.attendees.select_related(depth=1),
                                        #template_name=template_name,
                                        #default_to_empty_queryset=False,
                                        #extra_context={'event': event})

#def ajax_attendee_search(request, event_id):
    #return view_attendees(request,
                          #event_id,
                          #template_name='sadmin/events/ajax/attendee_search.html')

@sadmin_access_required
@permission_required('events.change_attend')
def view_attendee(request,
                  event_id,
                  attendee_id,
                  template_name='sadmin/events/event/attendee.html'):

    attendee = get_object_or_404(Attend, event=event_id, pk=attendee_id)

    # status

    if request.method == 'POST' and request.POST.get('submit_attendee', False):
        attendee_form = AttendeeForm(request.POST, instance=attendee)

        if attendee_form.is_valid():
            attendee_form.save()

        messages.success(request, u'%s status changed' % attendee.user)

    else:
        attendee_form = AttendeeForm(instance=attendee)

    # billing

    def create_payment():
        return Payment(revision=attendee.invoice.latest_revision,
                       amount=attendee.invoice.unpaid,
                       note=_('Paid at %(event)s') % {'event' : attendee.event.title})

    if request.method == 'POST' and request.POST.get('submit_payment', False):
        form = PaymentForm(request.POST, instance=create_payment())

        if form.is_valid():
            form.save()
            form = PaymentForm(instance=create_payment())

        messages.success(request, _(u'Payment registered for %s') % attendee.user)

    else:
        form = PaymentForm(instance=create_payment())

    # change selections

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

    return render_to_response(template_name,
                              {'event': attendee.event,
                               'attendee': attendee,
                               'attendee_form': attendee_form,
                               'option_forms' : option_forms,
                               'paymentform' : form,
                               'checkin_parts' : checkin_parts},
                              context_instance=SAdminContext(request))
