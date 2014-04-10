# coding=utf-8

from django.contrib.admin.util import NestedObjects
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.db.models import Count
from selvbetjening.core.members.models import UserLocation
from django.db import router

from selvbetjening.core.user.models import SUser
from selvbetjening.core.events.options.dynamic_selections import SCOPE, dynamic_selections_formset_factory, dynamic_selections
from selvbetjening.core.events.utils import sum_attendee_payment_status
from selvbetjening.core.events.models import Event, Attend, AttendState, Payment, AttendeeComment
from selvbetjening.core.events.signals import request_attendee_pks_signal

from selvbetjening.sadmin2.forms import EventForm, AttendeeFormattingForm, PaymentForm, \
    AttendeeCommentForm, attendee_selection_helper_factory, AttendeeCommentFormSet
from selvbetjening.sadmin2.decorators import sadmin_prerequisites
from selvbetjening.sadmin2 import menu

from generic import generic_create_view, search_view
from selvbetjening.sadmin2.graphs.timelines import AbsoluteTimeGraph, AgeTimeGraph
from selvbetjening.sadmin2.graphs.units import AttendeeRegisteredUnit, AttendeePaidUnit, AttendeeCheckedInUnit,\
    AttendeeRegisteredAgeUnit
from selvbetjening.sadmin2.views.reports import insecure_reports_address


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
            status_flat.setdefault(item['state'], 0)
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

    columns = ('pk', 'user__username', 'user__first_name', 'user__last_name', 'user__email',
               'user__street', 'user__postalcode', 'user__city')
    conditions = ('selection__option__pk', 'selection__suboption__pk', 'state', 'paid', 'price')

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
                       search_order='-pk',
                       context=context)


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

    graph = AbsoluteTimeGraph(AbsoluteTimeGraph.SCOPE.hour,
                              AttendeeCheckedInUnit('Checked-in', event),
                              accumulative=True)

    return render(request, 'sadmin2/graphs/linegraph.html', {
        'sadmin2_menu_main_active': 'events',
        'sadmin2_breadcrumbs_active': 'event_report_check_in',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
        'sadmin2_menu_tab_active': 'reports',
        'event': event,
        'title': _('Check-in'),
        'date_formatting': '%a %H:%M',
        'graph': graph
    })


@sadmin_prerequisites
def report_registration(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)

    graph = AbsoluteTimeGraph(AbsoluteTimeGraph.SCOPE.week,
                              AttendeeRegisteredUnit('Registered', event),
                              AttendeePaidUnit('Paid', event),
                              accumulative=True)

    return render(request, 'sadmin2/graphs/linegraph.html', {
        'sadmin2_menu_main_active': 'events',
        'sadmin2_breadcrumbs_active': 'event_report_registration',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
        'sadmin2_menu_tab_active': 'reports',
        'event': event,
        'title': _('Registrations'),
        'graph': graph
    })


@sadmin_prerequisites
def report_age(request, event_pk):

    event = get_object_or_404(Event, pk=event_pk)

    graph = AgeTimeGraph(AbsoluteTimeGraph.SCOPE.year,
                         AttendeeRegisteredAgeUnit('Users', event, event.startdate),
                         today=event.startdate)

    return render(request, 'sadmin2/graphs/linegraph.html', {
        'sadmin2_menu_main_active': 'events',
        'sadmin2_breadcrumbs_active': 'event_report_age',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
        'sadmin2_menu_tab_active': 'reports',
        'event': event,
        'title': _('User age'),
        'graph': graph
    })


@sadmin_prerequisites
def report_address(request, event_pk):

    event = get_object_or_404(Event, pk=event_pk)

    context = {
        'sadmin2_menu_main_active': 'events',
        'sadmin2_breadcrumbs_active': 'event_report_address',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
        'sadmin2_menu_tab_active': 'reports',

        'event': event
    }

    return insecure_reports_address(
        request,
        UserLocation.objects.filter(user__attend__event=event),
        extra_context=context
    )


@sadmin_prerequisites
def event_attendees_add(request, event_pk):

    event = get_object_or_404(Event, pk=event_pk)

    if request.method == 'POST':

        user = get_object_or_404(SUser, pk=int(request.POST.get('user_pk', 0)))
        Attend.objects.create(event=event, user=user)

        # TODO update this redirect to go directly to the attendee page when we have one
        messages.success(request, _('User %s added to event') % user.username)
        return HttpResponseRedirect(reverse('sadmin2:event_attendees', kwargs={'event_pk': event.pk}))

    queryset = SUser.objects.exclude(attend__event__pk=event.pk)
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

    comments = attendee.comments.filter(check_in_announce=True)
    selections = dynamic_selections(SCOPE.VIEW_SYSTEM_INVOICE, attendee)

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
                      'comments': comments,
                      'selections': selections
                  })


@sadmin_prerequisites
def event_attendee_payments(request, event_pk, attendee_pk):

    event = get_object_or_404(Event, pk=event_pk)
    attendee = get_object_or_404(event.attendees, pk=attendee_pk)

    payment_keys = request_attendee_pks_signal.send(None, attendee=attendee)
    payments = attendee.payment_set.all()

    context = {
        'sadmin2_menu_main_active': 'events',
        'sadmin2_breadcrumbs_active': 'event_attendees_attendee_payments',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_attendee,
        'sadmin2_menu_tab_active': 'payments',

        'event': event,
        'attendee': attendee,
        'payment_keys': payment_keys,
        'payments': payments,
    }

    def save_callback(payment):
        payment.note = 'Manual payment'
        payment.signee = request.user
        payment.attendee = attendee
        payment.user = attendee.user
        payment.save()

    return generic_create_view(
        request,
        PaymentForm,
        redirect_success_url=reverse('sadmin2:event_attendee_payments',
                                     kwargs={
                                         'event_pk': event.pk,
                                         'attendee_pk': attendee.pk
                                     }),
        message_success=_('Payment registered'),
        instance_save_callback=save_callback,
        template='sadmin2/event/attendee_payments.html',
        context=context
    )


@sadmin_prerequisites
def event_attendee_selections(request, event_pk, attendee_pk):

    event = get_object_or_404(Event, pk=event_pk)
    attendee = get_object_or_404(event.attendees, pk=attendee_pk)

    DynamicSelectionsFormSet = dynamic_selections_formset_factory(
        SCOPE.SADMIN,
        event,
        helper_factory=attendee_selection_helper_factory
    )

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

    if request.method == 'POST':

        formset = AttendeeCommentFormSet(request.POST, queryset=attendee.comments.all())

        if formset.is_valid():

            instances = formset.save(commit=False)
            for instance in instances:
                if instance.pk is None:
                    instance.attendee = attendee
                    instance.author = request.user

                instance.save()

            return HttpResponseRedirect(reverse('sadmin2:event_attendee_notes', kwargs={'event_pk': event.pk,
                                                                                        'attendee_pk': attendee.pk}))

    else:
        formset = AttendeeCommentFormSet(queryset=attendee.comments.all())

    context = {
        'sadmin2_menu_main_active': 'events',
        'sadmin2_breadcrumbs_active': 'event_attendees_attendee_notes',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_attendee,
        'sadmin2_menu_tab_active': 'notes',

        'event': event,
        'attendee': attendee,
        'comments': attendee.comments.all(),

        'formset': formset
    }

    return render(request,
                  'sadmin2/event/attendee_notes.html',
                  context)


def _get_deleted_objects(objs):
    """
    Slightly simplified version of the function used in the standard admin
    """

    if len(objs) == 0:
        return []

    collector = NestedObjects(using=router.db_for_write(objs[0]))
    collector.collect(objs)

    def format_callback(obj):
        return '%s: %s' % (obj.__class__.__name__, unicode(obj))

    return collector.nested(format_callback)


@sadmin_prerequisites
def event_attendee_delete(request, event_pk, attendee_pk):

    event = get_object_or_404(Event, pk=event_pk)
    attendee = get_object_or_404(event.attendees, pk=attendee_pk)

    if request.method == 'POST':
        attendee.delete()

        messages.success(request, _('Attendee %s deleted' % attendee.user.username))
        return HttpResponseRedirect(reverse('sadmin2:event_attendees', kwargs={'event_pk': event.pk}))

    context = {
        'sadmin2_menu_main_active': 'events',
        'sadmin2_breadcrumbs_active': 'event_attendees_attendee_delete',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_attendee,
        'sadmin2_menu_tab_active': 'delete',

        'event': event,
        'attendee': attendee,

        'to_be_deleted': _get_deleted_objects([attendee])
    }

    return render(request,
                  'sadmin2/event/attendee_delete.html',
                  context
                  )