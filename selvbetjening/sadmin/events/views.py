import operator

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.decorators import permission_required

from selvbetjening.data.events.models import Event, AttendState, Attend, AttendState
from selvbetjening.data.events.processor_handlers import change_selection_processors, checkin_processors
from selvbetjening.data.events.forms import PaymentForm, OptionForms
from selvbetjening.data.invoice.models import Invoice, Payment

from selvbetjening.sadmin.base.views import generic_search_page_unsecure
from selvbetjening.sadmin.base.sadmin import SAdminContext
from selvbetjening.sadmin.base.decorators import sadmin_access_required

from forms import CheckinForm, AttendeeForm, EventForm

@sadmin_access_required
@permission_required('events.change_event')
def list_events(request,
                template_name='sadmin/events/list.html'):

    return generic_search_page_unsecure(request,
                                        search_fields=('title', ),
                                        queryset=Event.objects.order_by('-startdate').all,
                                        template_name=template_name,
                                        default_to_empty_queryset=False)

def ajax_search(request):
    return list_events(request,
                       template_name='sadmin/events/ajax/search.html')

@sadmin_access_required
@permission_required('events.change_event')
def view_attendees(request,
                   event_id,
                   template_name='sadmin/events/event/attendees.html'):

    event = get_object_or_404(Event, pk=event_id)

    search_fields = ('user__first_name', 'user__last_name', 'user__username')

    return generic_search_page_unsecure(request,
                                        search_fields=search_fields,
                                        queryset=event.attendees.select_related(depth=1),
                                        template_name=template_name,
                                        default_to_empty_queryset=False,
                                        extra_context={'event': event})

def ajax_attendee_search(request, event_id):
    return view_attendees(request,
                          event_id,
                          template_name='sadmin/events/ajax/attendee_search.html')

@sadmin_access_required
@permission_required('events.change_event')
def view_statistics(request,
                    event_id,
                    template_name='sadmin/events/event/statistics.html'):

    event = get_object_or_404(Event, pk=event_id)

    statistics = {}

    event = get_object_or_404(Event, id=event_id)

    # attendees
    attendees_count = event.attendees.count()

    def attendee_statistics(state, identifier):
        attendees = event.attendees.filter(state=state)
        count = attendees.count()

        new = 0
        for attendee in attendees:
            if attendee.is_new():
                new += 1

        statistics[identifier + '_count'] = count
        statistics[identifier + '_new'] = new

        return new

    new_count = attendee_statistics(AttendState.waiting, 'waiting')
    new_count += attendee_statistics(AttendState.accepted, 'accepted')
    new_count += attendee_statistics(AttendState.attended, 'attended')

    # invoices
    statistics['invoice_payment_total'] = 0
    statistics['invoice_paid'] = 0

    statistics['invoices_in_balance'] = 0
    statistics['invoices_unpaid'] = 0
    statistics['invoices_partial'] = 0
    statistics['invoices_overpaid'] = 0
    statistics['invoices_count'] = 0

    for invoice in Invoice.objects.filter(attend__in=event.attendees):
        statistics['invoices_count'] += 1

        if invoice.in_balance():
            statistics['invoices_in_balance'] += 1

        if invoice.is_unpaid():
            statistics['invoices_unpaid'] += 1

        if invoice.is_overpaid():
            statistics['invoices_overpaid'] += 1

        if invoice.is_partial():
            statistics['invoices_partial'] += 1

        statistics['invoice_payment_total'] += invoice.total_price
        statistics['invoice_paid'] += invoice.paid

    # tilvalg

    optiongroups = []
    for optiongroup in event.optiongroup_set.all():
        options = []
        for option in optiongroup.option_set.all():
            count = option.selections.count()
            waiting = option.selections.filter(attendee__state=AttendState.waiting).count()
            accepted = option.selections.filter(attendee__state=AttendState.accepted).count()
            attended = option.selections.filter(attendee__state=AttendState.attended).count()
            options.append((option, count, waiting, accepted, attended))

        optiongroups.append((optiongroup, options))

    statistics.update({'event' : event,
                       'attendees_count' : attendees_count,
                       'new_count' : new_count,
                       'optiongroups' : optiongroups,})

    return render_to_response(template_name,
                              statistics,
                              context_instance=SAdminContext(request))

@sadmin_access_required
@permission_required('events.change_event')
def view(request,
         event_id,
         template_name='sadmin/events/event/view.html'):

    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'POST':
        form = None

        if form.is_valid():
            form.save()
            messages.success(request, _(u'Event updated'))
    else:
        form = None

    return render_to_response(template_name,
                              {'event' : event,
                               'form' : form},
                              context_instance=SAdminContext(request))

@sadmin_access_required
@permission_required('events.add_event')
def create(request,
           template_name='sadmin/events/event/create.html'):

    if request.method == 'POST':
        form = EventForm(request.POST)

        if form.is_valid():
            event = form.save()

        messages.success(request, _(u'Event created'))

        return HttpResponseRedirect(reverse('sadmin:events_view',
                                            kwargs={'event_id' : event.pk}))

    else:
        form = EventForm()

    return render_to_response(template_name,
                              {'form': form},
                              context_instance=SAdminContext(request))

@sadmin_access_required
@permission_required('events.change_event')
def update(request,
           event_id,
           template_name='sadmin/events/event/update.html'):

    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)

        if form.is_valid():
            form.save()

            messages.success(request, _(u'Event updated'))

    else:
        form = EventForm(instance=event)

    return render_to_response(template_name,
                              {'form': form,
                               'event': event},
                              context_instance=SAdminContext(request))

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
