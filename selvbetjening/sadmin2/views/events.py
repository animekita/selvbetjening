
import datetime
import time
from django.core.urlresolvers import reverse

from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect

from selvbetjening.core.events.models import Event, Attend, AttendState, Invoice, Selection, Option, OptionGroup, SubOption
from selvbetjening.sadmin.base import graph

from selvbetjening.sadmin2.forms import EventForm, InvoiceFormattingForm
from selvbetjening.sadmin2.decorators import sadmin_prerequisites

"""
    sadmin views

    Insert a view for each page you want to add.

    IMPORTANT: Prefix all views by @sadmin_prerequisites, this adds authentication and authorization to the views.

    You should add the following items to the view context for all rendered pages:

    sadmin2_menu_main_active: The ID of the currently active page in the main menu.
    sadmin2_breadcrumb_active: The ID of the current breadcrumb sequence you want to use.
"""

@sadmin_prerequisites
def event_list(request):

    return render(request,
                  'sadmin2/events/list.html',
                  {
                      'sadmin2_menu_main_active': 'events',
                      'sadmin2_breadcrumbs_active': 'events',
                      'events': Event.objects.all()
                  })

@sadmin_prerequisites
def event_attendees(request, event_pk):

    event = get_object_or_404(Event, pk=event_pk)

    return render(request,
                  'sadmin2/events/attendees/list.html',
                  {
                      'event': event,
                      'attendees': event.attendees.select_related('user', 'invoice'),
                      'sadmin2_menu_event_active': 'attendees'
                  })

@sadmin_prerequisites
def event_statistics(request, event_pk):

    event = get_object_or_404(Event, pk=event_pk)

    statistics = {}

    # attendees
    attendees = Attend.objects.all_related().filter(event=event_pk).prefetch_related('user__attend_set')
    attendees_count = attendees.count()

    def attendee_statistics(state, identifier):
        _attendees = attendees.filter(state=state)
        _count = _attendees.count()

        new = 0
        for attendee in _attendees:
            if attendee.is_new:
                new += 1

        statistics[identifier + '_count'] = _count
        statistics[identifier + '_new'] = new

        return new

    new_count = attendee_statistics(AttendState.waiting, 'waiting')
    new_count += attendee_statistics(AttendState.accepted, 'accepted')
    new_count += attendee_statistics(AttendState.attended, 'attended')

    # check-in graph

    _attendees = attendees.filter(state=AttendState.attended)\
        .filter(changed__gt=event.startdate)\
        .filter(changed__lt=event.startdate + datetime.timedelta(days=1))

    start = None
    end = None

    for attendee in _attendees:
        if start is None or attendee.changed < start:
            start = attendee.changed

        if end is None or attendee.changed > end:
            end = attendee.changed

    if start is not None:

        normalized_start_unix = time.mktime(datetime.datetime(start.year, start.month, start.day, start.hour).timetuple())
        end_unix = time.mktime(end.timetuple())

        slot_size = (60 * 10)  # 10 minute slots

        def get_slot(time_unix):
            return int((time_unix - normalized_start_unix) / slot_size)

        slots = get_slot(end_unix) + 1

        checkin_times = [0] * slots

        for attendee in _attendees:
            slot = get_slot(time.mktime(attendee.changed.timetuple()))
            checkin_times[slot] += 1

        checkin_axis = [''] * (slots + 1)

        for i in xrange(0, int(slots / 6) + 1):
            slot_time = datetime.datetime(start.year, start.month, start.day, start.hour) + datetime.timedelta(hours=i)
            checkin_axis[i * 6] = slot_time.strftime("%H:%M %x")

        statistics['checkin_axis'] = checkin_axis
        statistics['checkin_times'] = checkin_times

    else:
        statistics['checkin_axis'] = None
        statistics['checkin_times'] = None

    # attendees graph

    _attendees = attendees.filter(registration_date__isnull=False)

    if _attendees.count() > 0:

        first = _attendees.order_by('registration_date')[0].registration_date
        last = _attendees.order_by('-registration_date')[0].registration_date

        try:
            last_changed = _attendees.exclude(state=AttendState.waiting).order_by('-change_timestamp')[0].change_timestamp

            if last_changed > last:
                last = last_changed
        except IndexError:
            pass

        axis = graph.generate_week_axis(first, last)
        registration_data = [0] * len(axis)
        accepted_data = [0] * len(axis)

        for attendee in _attendees:
            week = graph.diff_in_weeks(first, attendee.registration_date)
            registration_data[week] += 1

            if attendee.state != AttendState.waiting:
                week = graph.diff_in_weeks(first, attendee.change_timestamp)
                accepted_data[week] += 1

        statistics['registrations_data'] = graph.insert_prefix(registration_data)
        statistics['registrations_data_acc'] = graph.accumulate(registration_data)
        statistics['accepted_data'] = graph.insert_prefix(accepted_data)
        statistics['accepted_data_acc'] = graph.accumulate(accepted_data)
        statistics['registrations_axis'] = graph.insert_prefix(axis, axis=True)

    # invoices
    statistics['invoice_payment_total'] = 0
    statistics['invoice_paid'] = 0

    statistics['invoices_in_balance'] = 0
    statistics['invoices_unpaid'] = 0
    statistics['invoices_partial'] = 0
    statistics['invoices_overpaid'] = 0
    statistics['invoices_count'] = 0

    invoices = Invoice.objects.select_related().\
                    prefetch_related('payment_set').\
                    prefetch_related('line_set').\
                    filter(attend__in=event.attendees)

    for invoice in invoices:
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

    statistics.update({'event': event,
                       'attendees_count': attendees_count,
                       'new_count': new_count,
                       'optiongroups': optiongroups,
                       'sadmin2_menu_event_active': 'statistics'})

    return render(request,
                  'sadmin2/events/statistics.html',
                  statistics)

@sadmin_prerequisites
def event_financial(request, event_pk):

    event = get_object_or_404(Event, pk=event_pk)

    invoice_queryset = Invoice.objects.select_related(). \
        prefetch_related('payment_set'). \
        prefetch_related('line_set'). \
        filter(attend__event=event)

    if request.method == 'POST' or 'event' in request.GET:
        formatting_form = InvoiceFormattingForm(request.REQUEST, invoices=invoice_queryset)
        formatting_form.is_valid()

    else:
        formatting_form = InvoiceFormattingForm(invoices=invoice_queryset)

    line_groups, total, detailed_view = formatting_form.format()

    return render(request,
                  'sadmin2/events/financial.html',
                  {
                      'invoices': invoice_queryset,
                      'line_groups': line_groups,
                      'total': total,
                      'detailed_view': detailed_view,
                      'formatting_form': formatting_form,
                      'event': event,
                      'sadmin2_menu_event_active': 'financial'
                  })

@sadmin_prerequisites
def event_settings_selections(request, event_pk):

    event = get_object_or_404(Event, pk=event_pk)

    return render(request,
                  'sadmin2/events/selections.html',
                  {
                      'event': event,
                      'sadmin2_menu_event_active': 'settings'
                  })

@sadmin_prerequisites
def event_settings(request, event_pk):

    event = get_object_or_404(Event, pk=event_pk)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)

        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, _('Settings saved successfully'))

    else:
        form = EventForm(instance=event)

    return render(request,
                  'sadmin2/events/settings.html',
                  {
                      'event': event,
                      'form': form,
                      'sadmin2_menu_event_active': 'settings'
                  })

@sadmin_prerequisites
def event_create(request):

    if request.method == 'POST':
        form = EventForm(request.POST)

        if form.is_valid():
            event = form.save()
            messages.add_message(request, messages.SUCCESS, _('Event created'))
            return HttpResponseRedirect(reverse('sadmin2:events_attendees_list', kwargs={'event_pk': event.pk}))

    else:
        form = EventForm()

    return render(request,
                  'sadmin2/events/create.html',
                  {
                      'form': form
                  })