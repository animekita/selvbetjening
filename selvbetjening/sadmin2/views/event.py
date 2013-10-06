
import datetime
import time

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.db.models import Count
from core.events.dynamic_selections import dynamic_selections, SCOPE, dynamic_selections_formset_factory
from core.events.utils import sum_attendee_payment_status

from selvbetjening.core.events.models import Event, Attend, AttendState, OptionGroup, Payment

from selvbetjening.sadmin2 import graph
from selvbetjening.sadmin2.forms import EventForm, AttendeeFormattingForm, OptionGroupForm, OptionForm, PaymentForm, \
    AttendeeCommentForm, attendee_selection_helper_factory
from selvbetjening.sadmin2.decorators import sadmin_prerequisites
from selvbetjening.sadmin2 import menu

from generic import generic_create_view, search_view


@sadmin_prerequisites
def event_overview(request, event_pk):

    event = get_object_or_404(Event, pk=event_pk)

    total = sum_attendee_payment_status(event.attendees)

    # returns a set of dictionaries with {'state': x, 'is_new': y, 'count': z}
    status = Attend.objects.filter(event=event).values('state', 'is_new').annotate(count=Count('pk'))
    status_flat = {}

    for item in status:
        status_flat['%s_new' % item['state'] if item['is_new'] else item['state']] = item['count']

    for item in status:
        if item['is_new']:
            status_flat[item['state']] += item['count']

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

    queryset = event.attendees.select_related('user').all()

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

    # TODO rewrite this to use annotations to reduce the number of db queries

    option_groups = []
    for option_group in event.optiongroups.prefetch_related('option_set'):
        options = []
        for option in option_group.option_set.all():
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
def event_selections_manage(request, event_pk):

    FIELDS = (
        'selected_by_default',
        'in_scope_view_registration',
        'in_scope_view_manage',
        'in_scope_view_user_invoice',
        'in_scope_view_system_invoice',
        'in_scope_edit_registration',
        'in_scope_edit_manage_waiting',
        'in_scope_edit_manage_accepted',
        'in_scope_edit_manage_attended',
        'order'
    )

    GROUP_FIELDS = (
        'order',
    )

    event = get_object_or_404(Event, pk=event_pk)
    option_groups = event.optiongroups

    # Note, we could have used the standard django form framework for this, however it would be a mess
    # I only hope this is just a bit less messy :)

    if request.method == 'POST':

        # add anon option group

        if 'add-anon-group' in request.POST:

            if not event.has_special:

                OptionGroup.objects.create(
                    event=event,
                    is_special=True
                )

                messages.success(request, _('Special option group created'))
                return HttpResponseRedirect(reverse('sadmin2:event_selections_manage', kwargs={'event_pk': event.pk}))

        # split selections into options

        option_data = {}
        option_group_data = {}

        for key, value in request.POST.items():

            # all option data is formatted as field__pk and option_group data is formatted as field--pk
            if '__' in key:
                split = '__'
                data = option_data
            elif '--' in key:
                split = '--'
                data = option_group_data
            else:
                continue

            field, pk = key.split(split)
            pk = int(pk)

            data.setdefault(pk, {})
            data[pk][field] = value

        # update options

        def inject_data(object, fields, data):
            for field in fields:
                if field == 'order':
                    try:
                        setattr(object, field, int(data[object.pk][field]))
                    except KeyError:
                        pass  # race condition on new option?
                else:
                    setattr(object, field, object.pk in data and field in data[object.pk])

        for option_group in option_groups:

            inject_data(option_group, GROUP_FIELDS, option_group_data)
            option_group.save()

            for option in option_group.options:
                inject_data(option, FIELDS, option_data)
                option.save()

        messages.success(request, _('Selections saves'))
        return HttpResponseRedirect(reverse('sadmin2:event_selections_manage', kwargs={'event_pk': event.pk}))

    return render(request,
                  'sadmin2/event/selections_manage.html',
                  {
                      'sadmin2_menu_main_active': 'events',
                      'sadmin2_breadcrumbs_active': 'event_selections_manage',
                      'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
                      'sadmin2_menu_tab_active': 'selections',

                      'event': event,

                      'option_groups': option_groups
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
                               reverse('sadmin2:event_selections_manage', kwargs={'event_pk': event.pk}),
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
                               reverse('sadmin2:event_selections_manage', kwargs={'event_pk': event.pk}),
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
                               reverse('sadmin2:event_selections_manage', kwargs={'event_pk': event.pk}),
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
                               reverse('sadmin2:event_selections_manage', kwargs={'event_pk': event.pk}),
                               message_success=_('Option saved'),
                               context=context,
                               instance=option)

@sadmin_prerequisites
def event_account(request, event_pk):

    event = get_object_or_404(Event, pk=event_pk)

    if request.method == 'POST':
        formatting_form = AttendeeFormattingForm(request.REQUEST, event=event, attendees=event.attendees)
        formatting_form.is_valid()
    else:
        formatting_form = AttendeeFormattingForm(event=event, attendees=event.attendees)

    attendees, line_groups, total, show_regular_attendees, show_irregular_attendees, attendee_filter_label = formatting_form.format()

    return render(request,
                  'sadmin2/event/account.html',
                  {
                      'sadmin2_menu_main_active': 'event',
                      'sadmin2_breadcrumbs_active': 'event_account',
                      'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
                      'sadmin2_menu_tab_active': 'account',

                      'event': event,
                      'attendees': attendees.order_by('user__username'),

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
        Attend.objects.create(event=event, user=user)

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

    selections = dynamic_selections(SCOPE.VIEW_SYSTEM_INVOICE, event, attendee)

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
                user=attendee.user,
                attendee=attendee,
                amount=attendee.unpaid,
                note='Manual payment',
                signee=request.user
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
                      'attendee': attendee,
                      'selections': selections
                  })

@sadmin_prerequisites
def event_attendee_payments(request, event_pk, attendee_pk):

    event = get_object_or_404(Event, pk=event_pk)
    attendee = get_object_or_404(event.attendees, pk=attendee_pk)

    payments = attendee.payment_set.all()

    if request.method == 'POST':

        form = PaymentForm(request.POST)

        if form.is_valid():

            payment = form.save(commit=False)
            payment.note = 'Manual payment'
            payment.signee = request.user
            payment.attendee = attendee
            payment.user = attendee.user
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
def event_attendee_selections(request, event_pk, attendee_pk):

    event = get_object_or_404(Event, pk=event_pk)
    attendee = get_object_or_404(event.attendees, pk=attendee_pk)

    DynamicSelectionsFormSet = dynamic_selections_formset_factory(
        event,
        helper_factory=attendee_selection_helper_factory)

    if request.method == 'POST':
        formset = DynamicSelectionsFormSet(request.POST, attendee=attendee)

        if formset.is_valid():

            formset.save()

            messages.success(request, 'Saved selections')
            return HttpResponseRedirect(reverse('sadmin2:event_attendee', kwargs={'event_pk': event.pk,
                                                                                  'attendee_pk': attendee.pk}))
    else:
        formset = DynamicSelectionsFormSet(attendee=attendee)

    return render(request,
                  'sadmin2/event/attendee_selections.html',
                  {
                      'sadmin2_menu_main_active': 'events',
                      'sadmin2_breadcrumbs_active': 'event_attendees_attendee_selections',
                      'sadmin2_menu_tab': menu.sadmin2_menu_tab_attendee,
                      'sadmin2_menu_tab_active': 'selections',

                      'event': event,
                      'attendee': attendee,

                      'formset': formset
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
