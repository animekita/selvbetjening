
import datetime
import time

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.db.models import Count
from core.invoice.models import Payment

from selvbetjening.core.events.models import Event, Attend, AttendState, Invoice
from selvbetjening.core.invoice.utils import sum_invoices

from selvbetjening.sadmin.base import graph
from selvbetjening.sadmin2.forms import EventForm, InvoiceFormattingForm, OptionGroupForm, OptionForm, PaymentForm, AttendeeCommentForm
from selvbetjening.sadmin2.decorators import sadmin_prerequisites
from selvbetjening.sadmin2 import menu

from generic import generic_create_view, search_view


@sadmin_prerequisites
def event_overview(request, event_pk):

    event = get_object_or_404(Event, pk=event_pk)

    invoices = Invoice.objects.select_related().\
        prefetch_related('payment_set').\
        prefetch_related('line_set').\
        filter(attend__in=event.attendees)

    total = sum_invoices(invoices)

    # returns a set of dictionaries with {'state': x, 'is_new': y, 'count': z}
    status = Attend.objects.all().values('state', 'is_new').annotate(count=Count('pk'))
    status_flat = {}

    for item in status:
        status_flat['%s_new' % item['state'] if item['is_new'] else item['state']] = item['count']

    return render(request,
                  'sadmin2/event/overview.html',
                  {
                      'sadmin2_menu_main_active': 'events',
                      'sadmin2_breadcrumbs_active': 'event',
                      'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
                      'sadmin2_menu_tab_active': 'overview',

                      'event': event,
                      'total': total,
                      'status': status_flat
                  })

@sadmin_prerequisites
def event_attendees(request, event_pk):

    event = get_object_or_404(Event, pk=event_pk)

    columns = ('user__username', 'user__first_name', 'user__last_name', 'user__email')
    conditions = ('selection__option__pk', 'state')

    queryset = event.attendees.select_related('user', 'invoice').all()

    context = {
        'sadmin2_menu_main_active': 'events',
        'sadmin2_breadcrumbs_active': 'event_attendees',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
        'sadmin2_menu_tab_active': 'attendees',

        'event': event
    }

    return search_view(request,
                       queryset,
                       'sadmin2/event/attendees.html',
                       'sadmin2/event/attendees_inner.html',
                       search_columns=columns,
                       search_conditions=conditions,
                       context=context)

@sadmin_prerequisites
def event_selections(request, event_pk):

    event = get_object_or_404(Event, pk=event_pk)

    if request.method == 'POST':

        inline_action = request.POST.get('inline-action', '')

        # Handle option group reordering

        if inline_action == 'move-group':
            # We calculate the new order as follows:
            # - Iterate over the current list of groups and reassign new order numbers.
            # - The order starts with 0 and increments with 2 for each group.
            # - The group being moved up or down is modified with a 3 or -3 modifier,
            #   in practice moving it up and down the order

            # by default order is ordered in ascending order

            modifier = 3 if 'down' in request.POST.get('direction', 'up') else -3
            option_group_pk = int(request.POST.get('option_group_pk', 0))

            order = 0
            for option_group in event.optiongroups:
                modified_order = order if option_group.pk != option_group_pk else order + modifier

                option_group.order = modified_order
                option_group.save()

                order += 2

        if inline_action == 'move-option':

            modifier = 3 if 'down' in request.POST.get('direction', 'up') else -3
            option_group_pk = int(request.POST.get('option_group_pk', 0))
            option_pk = int(request.POST.get('option_pk', 0))

            option_group = get_object_or_404(event.optiongroups, pk=option_group_pk)

            order = 0
            for option in option_group.options:
                modified_order = order if option.pk != option_pk else order + modifier

                option.order = modified_order
                option.save()

                order += 2

    # Statistics

    option_groups = []
    for option_group in event.optiongroups:
        options = []
        for option in option_group.options:
            count = option.selections.count()
            waiting = option.selections.filter(attendee__state=AttendState.waiting).count()
            accepted = option.selections.filter(attendee__state=AttendState.accepted).count()
            attended = option.selections.filter(attendee__state=AttendState.attended).count()
            options.append((option, count, waiting, accepted, attended))

        option_groups.append((option_group, options))

    return render(request,
                  'sadmin2/event/selections.html',
                  {
                      'sadmin2_menu_main_active': 'events',
                      'sadmin2_breadcrumbs_active': 'event_selections',
                      'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
                      'sadmin2_menu_tab_active': 'selections',

                      'event': event,

                      'optiongroups': option_groups
                  })

@sadmin_prerequisites
def event_selections_create_group(request, event_pk):

    event = get_object_or_404(Event, pk=event_pk)

    context = {
        'sadmin2_menu_main_active': 'events',
        'sadmin2_breadcrumbs_active': 'event_selections_create_group',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
        'sadmin2_menu_tab_active': 'selections',

        'event': event
    }

    def save_callback(instance):
        instance.event = event
        instance.save()

    return generic_create_view(request,
                               OptionGroupForm,
                               reverse('sadmin2:event_selections', kwargs={'event_pk': event.pk}),
                               message_success=_('Option group created'),
                               context=context,
                               instance_save_callback=save_callback)

@sadmin_prerequisites
def event_selections_edit_group(request, event_pk, group_pk):

    event = get_object_or_404(Event, pk=event_pk)
    group = get_object_or_404(event.optiongroups, pk=group_pk)

    context = {
        'sadmin2_menu_main_active': 'events',
        'sadmin2_breadcrumbs_active': 'event_selections_edit_group',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
        'sadmin2_menu_tab_active': 'selections',

        'event': event,
        'option_group': group
    }

    return generic_create_view(request,
                               OptionGroupForm,
                               reverse('sadmin2:event_selections', kwargs={'event_pk': event.pk}),
                               message_success=_('Option group saved'),
                               context=context,
                               instance=group)

@sadmin_prerequisites
def event_selections_create_option(request, event_pk, group_pk):

    event = get_object_or_404(Event, pk=event_pk)
    group = get_object_or_404(event.optiongroups, pk=group_pk)

    context = {
        'sadmin2_menu_main_active': 'events',
        'sadmin2_breadcrumbs_active': 'event_selections_create_option',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
        'sadmin2_menu_tab_active': 'selections',

        'event': event,
        'option_group': group
    }

    def save_callback(instance):
        instance.group = group
        instance.save()

    return generic_create_view(request,
                               OptionForm,
                               reverse('sadmin2:event_selections', kwargs={'event_pk': event.pk}),
                               message_success=_('Option created'),
                               context=context,
                               instance_save_callback=save_callback)


@sadmin_prerequisites
def event_selections_edit_option(request, event_pk, group_pk, option_pk):

    event = get_object_or_404(Event, pk=event_pk)
    group = get_object_or_404(event.optiongroups, pk=group_pk)
    option = get_object_or_404(group.options, pk=option_pk)

    context = {
        'sadmin2_menu_main_active': 'events',
        'sadmin2_breadcrumbs_active': 'event_selections_edit_option',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
        'sadmin2_menu_tab_active': 'selections',

        'event': event,
        'option_group': group,
        'option': option
    }

    return generic_create_view(request,
                               OptionForm,
                               reverse('sadmin2:event_selections', kwargs={'event_pk': event.pk}),
                               message_success=_('Option saved'),
                               context=context,
                               instance=option)

@sadmin_prerequisites
def event_account(request, event_pk):

    event = get_object_or_404(Event, pk=event_pk)

    invoice_queryset = Invoice.objects.select_related(). \
        prefetch_related('payment_set'). \
        prefetch_related('line_set'). \
        filter(attend__event=event)

    if request.method == 'POST':
        formatting_form = InvoiceFormattingForm(request.REQUEST, invoices=invoice_queryset)
        formatting_form.is_valid()
    else:
        formatting_form = InvoiceFormattingForm(invoices=invoice_queryset)

    invoices, line_groups, total, show_regular_attendees, show_irregular_attendees, attendee_filter_label = formatting_form.format()

    return render(request,
                  'sadmin2/event/account.html',
                  {
                      'sadmin2_menu_main_active': 'event',
                      'sadmin2_breadcrumbs_active': 'event_account',
                      'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
                      'sadmin2_menu_tab_active': 'account',

                      'event': event,
                      'invoices': invoices.order_by('user__username'),

                      'line_groups': line_groups,
                      'total': total,

                      'show_regular_attendees': show_regular_attendees,
                      'show_irregular_attendees': show_irregular_attendees,

                      'formatting_form': formatting_form,
                      'attendee_filter_label': attendee_filter_label
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
                  'sadmin2/generic/form.html',
                  {
                      'sadmin2_menu_main_active': 'events',
                      'sadmin2_breadcrumbs_active': 'event_settings',
                      'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
                      'sadmin2_menu_tab_active': 'settings',

                      'event': event,
                      'form': form
                  })


@sadmin_prerequisites
def report_check_in(request, event_pk):

    event = get_object_or_404(Event, pk=event_pk)
    attendees = event.attendees

    menu_decl = {
        'sadmin2_menu_main_active': 'events',
        'sadmin2_breadcrumbs_active': 'event_report_check_in',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
        'sadmin2_menu_tab_active': 'reports',

        'event': event
    }

    if event.startdate is None or event.enddate is None:

        menu_decl.update({
            'subject': _('Event start and end time missing'),
            'message': _('Please update the settings for this event.')
        })

        return render(request,
                      'sadmin2/generic/error.html',
                      menu_decl)

    attendees = attendees.filter(state=AttendState.attended)\
                         .filter(changed__gt=event.startdate)\
                         .filter(changed__lt=event.startdate + datetime.timedelta(days=1))

    if attendees.count() == 0:

        menu_decl.update({
            'subject': _('No attendees checked in'),
            'message': _('Please wait until at least one attendee has checked in.')
        })

        return render(request,
                      'sadmin2/generic/error.html',
                      menu_decl)

    # find first and last changed time

    start = None
    end = None

    for attendee in attendees:
        if start is None or attendee.changed < start:
            start = attendee.changed

        if end is None or attendee.changed > end:
            end = attendee.changed

    normalized_start_unix = time.mktime(datetime.datetime(start.year, start.month, start.day, start.hour).timetuple())
    end_unix = time.mktime(end.timetuple())

    slot_size = (60 * 10)  # 10 minute slots

    def get_slot(time_unix):
        return int((time_unix - normalized_start_unix) / slot_size)

    slots = get_slot(end_unix) + 1

    checkin_times = [0] * slots

    for attendee in attendees:
        slot = get_slot(time.mktime(attendee.changed.timetuple()))
        checkin_times[slot] += 1

    checkin_axis = [''] * (slots + 1)

    for i in xrange(0, int(slots / 6) + 1):
        slot_time = datetime.datetime(start.year, start.month, start.day, start.hour) + datetime.timedelta(hours=i)
        checkin_axis[i * 6] = slot_time.strftime("%H:%M %x")

    menu_decl.update({
        'checkin_axis': checkin_axis,
        'checkin_times':  checkin_times
    })

    return render(request,
                  'sadmin2/event/report_check_in.html',
                  menu_decl)


@sadmin_prerequisites
def report_registration(request, event_pk):

    event = get_object_or_404(Event, pk=event_pk)

    attendees = event.attendees
    attendees = attendees.filter(registration_date__isnull=False)

    menu_decl = {
        'sadmin2_menu_main_active': 'events',
        'sadmin2_breadcrumbs_active': 'event_report_registration',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
        'sadmin2_menu_tab_active': 'reports',

        'event': event
    }

    if attendees.count() == 0:

        menu_decl.update({
            'subject': _('No attendees'),
            'message': _('Wait until some people have registered for the event.')
        })

        return render(request,
                      'sadmin2/generic/error.html',
                      menu_decl)

    first = attendees.order_by('registration_date')[0].registration_date
    last = attendees.order_by('-registration_date')[0].registration_date

    try:
        last_changed = attendees.exclude(state=AttendState.waiting).order_by('-change_timestamp')[0].change_timestamp

        if last_changed > last:
            last = last_changed
    except IndexError:
        pass

    axis = graph.generate_week_axis(first, last)
    registration_data = [0] * len(axis)
    accepted_data = [0] * len(axis)

    for attendee in attendees:
        week = graph.diff_in_weeks(first, attendee.registration_date)
        registration_data[week] += 1

        if attendee.state != AttendState.waiting:
            week = graph.diff_in_weeks(first, attendee.change_timestamp)
            accepted_data[week] += 1

    menu_decl.update({
        'registrations_data': graph.insert_prefix(registration_data),
        'registrations_data_acc': graph.accumulate(registration_data),
        'accepted_data': graph.insert_prefix(accepted_data),
        'accepted_data_acc': graph.accumulate(accepted_data),
        'registrations_axis': graph.insert_prefix(axis, axis=True)
    })

    return render(request,
                  'sadmin2/event/report_registration.html',
                  menu_decl)


@sadmin_prerequisites
def event_attendees_add(request, event_pk):

    event = get_object_or_404(Event, pk=event_pk)

    if request.method == 'POST':

        user = get_object_or_404(User, pk=int(request.POST.get('user_pk', 0)))
        event.add_attendee(user)

        # TODO update this redirect to go directly to the attendee page when we have one
        messages.success(request, _('User %s added to event') % user.username)
        return HttpResponseRedirect(reverse('sadmin2:event_attendees', kwargs={'event_pk': event.pk}))

    queryset = User.objects.exclude(attend__event__pk=event.pk)
    columns = ('username', 'first_name', 'last_name', 'email')

    context = {
        'sadmin2_menu_main_active': 'events',
        'sadmin2_breadcrumbs_active': 'event_attendees_add',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
        'sadmin2_menu_tab_active': 'attendees',

        'event': event,
    }

    return search_view(request,
                       queryset,
                       'sadmin2/event/attendees_add.html',
                       'sadmin2/event/attendees_add_inner.html',
                       search_columns=columns,
                       context=context
                       )

@sadmin_prerequisites
def event_attendee(request, event_pk, attendee_pk):

    event = get_object_or_404(Event, pk=event_pk)
    attendee = get_object_or_404(event.attendees, pk=attendee_pk)

    if request.method == 'POST':

        action = request.POST.get('action', '')

        if action == 'to-state-waiting':
            attendee.state = AttendState.waiting
            attendee.save()

        if action == 'to-state-accepted':
            attendee.state = AttendState.accepted
            attendee.save()

        if action == 'to-state-attended':
            attendee.state = AttendState.attended
            attendee.save()

        if action == 'pay':

            Payment.objects.create(
                amount=attendee.invoice.unpaid,
                note='Manual payment',
                signee=request.user,
                invoice=attendee.invoice
            )

            return HttpResponseRedirect(reverse('sadmin2:event_attendee', kwargs={'event_pk': event.pk, 'attendee_pk': attendee.pk}))

    return render(request,
                  'sadmin2/event/attendee.html',
                  {
                      'sadmin2_menu_main_active': 'events',
                      'sadmin2_breadcrumbs_active': 'event_attendees_attendee',
                      'sadmin2_menu_tab': menu.sadmin2_menu_tab_attendee,
                      'sadmin2_menu_tab_active': 'registration',

                      'event': event,
                      'attendee': attendee
                  })

@sadmin_prerequisites
def event_attendee_payments(request, event_pk, attendee_pk):

    event = get_object_or_404(Event, pk=event_pk)
    attendee = get_object_or_404(event.attendees, pk=attendee_pk)

    payments = attendee.invoice.payment_set.all()

    if request.method == 'POST':

        form = PaymentForm(request.POST)

        if form.is_valid():

            payment = form.save(commit=False)
            payment.note = 'Manual payment'
            payment.signee = request.user
            payment.invoice = attendee.invoice
            payment.save()

            messages.success(request, _('Payment registered'))
            return HttpResponseRedirect(reverse('sadmin2:event_attendee_payments', kwargs={'event_pk': event.pk, 'attendee_pk': attendee.pk}))

    else:
        form = PaymentForm()

    return render(request,
                  'sadmin2/event/attendee_payments.html',
                  {
                      'sadmin2_menu_main_active': 'events',
                      'sadmin2_breadcrumbs_active': 'event_attendees_attendee_payments',
                      'sadmin2_menu_tab': menu.sadmin2_menu_tab_attendee,
                      'sadmin2_menu_tab_active': 'payments',

                      'event': event,
                      'attendee': attendee,
                      'payments': payments,

                      'form': form
                  })

@sadmin_prerequisites
def event_attendee_notes(request, event_pk, attendee_pk):

    event = get_object_or_404(Event, pk=event_pk)
    attendee = get_object_or_404(event.attendees, pk=attendee_pk)

    notes = attendee.comments

    context = {
        'sadmin2_menu_main_active': 'events',
        'sadmin2_breadcrumbs_active': 'event_attendees_attendee_notes',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_attendee,
        'sadmin2_menu_tab_active': 'notes',

        'event': event,
        'attendee': attendee,
        'notes': notes.all()
    }

    def save_callback(instance):
        instance.attendee = attendee
        instance.author = request.user
        instance.save()

    return generic_create_view(request,
                               AttendeeCommentForm,
                               reverse('sadmin2:event_attendee_notes', kwargs={'event_pk': event.pk, 'attendee_pk': attendee.pk}),
                               context=context,
                               instance_save_callback=save_callback,
                               template='sadmin2/event/attendee_notes.html'
                               )
