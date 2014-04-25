# coding=UTF-8

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db.models.aggregates import Count
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from django.contrib import messages

from selvbetjening.core.events.options.dynamic_selections import dynamic_statistics, dynamic_selections_formset_factory, SCOPE, dynamic_selections
from selvbetjening.core.events.models import Event, Attend, AttendState, AttendeeAcceptPolicy

from selvbetjening.businesslogic.events import decorators as eventdecorators
from selvbetjening.businesslogic.events.decorators import suspend_automatic_attendee_price_updates
from selvbetjening.core.events.signals import attendee_updated_signal
from selvbetjening.frontend.base.views.events import generic_event_status

from selvbetjening.sadmin2.forms import attendee_selection_helper_factory


def events_list(request,
                template_name='eventportal/list.html'):

    return render(request,
                  template_name,
                  {
                      'events': Event.objects.order_by('-startdate')
                  })


def event_detail(request,
          event_pk,
          template_name='eventportal/event.html'):

    event = get_object_or_404(Event, pk=event_pk)

    try:
        if request.user.is_authenticated():
            attendee = Attend.objects.get(event=event, user=request.user)
        else:
            attendee = None
    except Attend.DoesNotExist:
        attendee = None

    # Attendee stats

    attendee_stats = {}

    for item in event.attendees.values('state').annotate(count=Count('pk')):
        attendee_stats[item['state']] = item['count']

    attendee_stats['accepted'] = attendee_stats.get('accepted', 0) + attendee_stats.get('attended', 0)
    attendee_stats.setdefault('waiting', 0)

    if 'attended' in attendee_stats:
        del attendee_stats['attended']

    # Options stats

    public_options = dynamic_statistics(event)

    return render(request,
                  template_name,
                  {
                      'event': event,
                      'is_attendee': attendee is not None,
                      'attendee': attendee,
                      'attendee_stats': attendee_stats,
                      'public_options': public_options,
                      'waiting_attendees': event.attendees.filter(state=AttendState.waiting).select_related('user'),
                      'confirmed_attendees': event.attendees.exclude(state=AttendState.waiting).select_related('user')
                  })


@login_required
@eventdecorators.get_event_from_id
@eventdecorators.event_registration_open_required
@suspend_automatic_attendee_price_updates
def event_register(request,
                   event,
                   template='eventportal/event_register.html',
                   extra_context=None):

    # TODO This method should be merged with the nearly identical registration method in eventsingle

    if extra_context is None:
        extra_context = {}

    EventSelectionFormSet = dynamic_selections_formset_factory(
        SCOPE.EDIT_REGISTRATION,
        event,
        helper_factory=attendee_selection_helper_factory
    )

    if event.is_attendee(request.user):
        return HttpResponseRedirect(
            reverse('eventportal_event_status',
                    kwargs={'event_pk': event.pk}))

    if request.method == 'POST':
        options_form = EventSelectionFormSet(request.POST, user=request.user)

        if options_form.is_valid():

            attendee = Attend.objects.create(event=event, user=request.user, price=0)
            options_form.save(attendee=attendee)

            attendee.recalculate_price()

            attendee.event.send_notification_on_registration(attendee)

            # If the user has paid fully, and the event policy is to move paid members to the attended state, then do it
            if event.move_to_accepted_policy == AttendeeAcceptPolicy.on_payment and attendee.is_paid():
                attendee.state = AttendState.accepted
                attendee.save()

            messages.success(request, _(u'You are now registered for this event.'))

            attendee_updated_signal.send(event_register, attendee=attendee)

            return HttpResponseRedirect(
                reverse('eventportal_event', kwargs={'event_pk': event.pk}) + '?signup=1')

    else:
        options_form = EventSelectionFormSet(user=request.user)

    context = {
        'event': event,
        'formset': options_form,
    }
    context.update(extra_context)

    return render(request,
                  template,
                  context)


@login_required
@eventdecorators.get_event_from_id
@eventdecorators.event_registration_open_required
@eventdecorators.event_attendance_required
@suspend_automatic_attendee_price_updates
def event_unregister(request, event):

    attendee = get_object_or_404(Attend, user=request.user, event=event)

    if attendee.state != AttendState.waiting:
        return HttpResponseForbidden()

    if request.method == 'POST':
        attendee.delete()
        messages.success(request, _(u'You are now removed from the event.'))

        return HttpResponseRedirect(
            reverse('eventportal_event', kwargs={'event_pk': event.pk}))

    return render(request,
                  'eventportal/unregister.html',
                  {})


@login_required
@eventdecorators.get_event_from_id
@eventdecorators.event_registration_open_required
@eventdecorators.event_attendance_required
@suspend_automatic_attendee_price_updates
def event_status_update(request, event):

    attendee = Attend.objects.get(user=request.user, event=event)

    if attendee.state == AttendState.waiting:
        scope = SCOPE.EDIT_MANAGE_WAITING
    elif attendee.state == AttendState.accepted:
        scope = SCOPE.EDIT_MANAGE_ACCEPTED
    else:
        scope = SCOPE.EDIT_MANAGE_ATTENDED

    EventSelectionFormSet = dynamic_selections_formset_factory(
        scope,
        event,
        helper_factory=attendee_selection_helper_factory
    )

    if request.method == 'POST':

        form = EventSelectionFormSet(request.POST, user=request.user, attendee=attendee)

        if form.is_valid():
            form.save()
            attendee.recalculate_price()

            # If the user has paid fully, and the event policy is to move paid members to the attended state, then do it
            if event.move_to_accepted_policy == AttendeeAcceptPolicy.on_payment and attendee.is_paid():
                attendee.state = AttendState.accepted
                attendee.save()

            attendee.event.send_notification_on_registration_update(attendee)

            attendee_updated_signal.send(event_status_update, attendee=attendee)

            return HttpResponseRedirect(
                reverse('eventportal_event_status',
                        kwargs={'event_pk': event.id}))

    else:
        form = EventSelectionFormSet(user=request.user, attendee=attendee)

    return render(request,
                  'eventportal/status_update.html',
                  {
                      'event': event,
                      'formset': form
                  })


@login_required
@eventdecorators.get_event_from_id
@eventdecorators.event_attendance_required
def event_status(request,
                 event,
                 template_name='eventportal/status.html',
                 extra_context=None):

    return generic_event_status(request, event, template_name, extra_context)
