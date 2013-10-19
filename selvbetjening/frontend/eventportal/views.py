# coding=UTF-8

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db.models.aggregates import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import Context, Template
from django.utils.translation import ugettext as _
from django.contrib import messages
from businesslogic.events import decorators as eventdecorators
from core.events.dynamic_selections import dynamic_statistics, dynamic_selections_formset_factory, SCOPE
from sadmin2.forms import attendee_selection_helper_factory

from selvbetjening.core.events.models import Event, Attend, AttendState
from businesslogic.events.decorators import suspend_automatic_attendee_price_updates


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

    instance = get_object_or_404(Event, pk=event_pk)

    # Attendee stats

    attendee_stats = {}

    for item in instance.attendees.values('state').annotate(count=Count('pk')):
        attendee_stats[item['state']] = item['count']

    attendee_stats['accepted'] = attendee_stats.get('accepted', 0) + attendee_stats.get('attended', 0)
    attendee_stats.setdefault('waiting', 0)

    if 'attended' in attendee_stats:
        del attendee_stats['attended']

    # Options stats

    public_options = dynamic_statistics(instance)

    return render(request,
                  template_name,
                  {
                      'event': instance,
                      'is_attendee': instance.is_attendee(request.user),
                      'attendee_stats': attendee_stats,
                      'public_options': public_options,
                      'waiting_attendees': instance.attendees.filter(state=AttendState.waiting).select_related('user'),
                      'confirmed_attendees': instance.attendees.exclude(state=AttendState.waiting).select_related('user')
                  })


@login_required
@eventdecorators.get_event_from_id
@eventdecorators.event_registration_open_required
@suspend_automatic_attendee_price_updates
def event_register(request,
                   event):

    EventSelectionFormSet = dynamic_selections_formset_factory(
        SCOPE.VIEW_REGISTRATION,
        event,
        helper_factory=attendee_selection_helper_factory
    )

    if event.is_attendee(request.user):
        return HttpResponseRedirect(
            reverse('eventportal_event_status',
                    kwargs={'event_pk': event.pk}))

    if request.method == 'POST':
        options_form = EventSelectionFormSet(request.POST)

        if options_form.is_valid():

            attendee = Attend.objects.create(event=event, user=request.user, price=0)
            options_form.save(attendee=attendee)

            attendee.recalculate_price()

            attendee.event.send_notification_on_registration(attendee)

            return HttpResponseRedirect(
                reverse('eventportal_event', kwargs={'event_pk': event.pk}) + '?signup=1')

    else:
        options_form = EventSelectionFormSet()

    return render(request,
                  'eventportal/event_register.html',
                  {
                      'formset': options_form,
                  })

@login_required
@eventdecorators.get_event_from_id
@eventdecorators.event_registration_open_required
@eventdecorators.event_attendance_required
@suspend_automatic_attendee_price_updates
def event_unregister(request, event):

    attendee = Attend.objects.get(user=request.user, event=event)

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

    # TODO select an appropriate scope
    EventSelectionFormSet = dynamic_selections_formset_factory(
        SCOPE.VIEW_MANAGE,
        event,
        helper_factory=attendee_selection_helper_factory
    )

    if request.method == 'POST':

        form = EventSelectionFormSet(request.POST, attendee=attendee)

        if form.is_valid():
            form.save()
            attendee.recalculate_price()
            attendee.event.send_notification_on_registration_update(attendee)

            return HttpResponseRedirect(
                reverse('eventportal_event_status',
                        kwargs={'event_pk': event.id}))

    else:
        form = EventSelectionFormSet(attendee=attendee)

    return render(request,
                  'eventportal/status_update.html',
                  {
                      'formset': form
                  })

@login_required
@eventdecorators.get_event_from_id
@eventdecorators.event_attendance_required
def event_status(request, event):

    attendee = Attend.objects.get(user=request.user, event=event)

    context = {'event': event,
                     'user': attendee.user,
                     'attendee': attendee}

    context = Context(context)

    custom_status_page = None
    if event.show_custom_status_page:
        template = Template(event.custom_status_page)
        custom_status_page = template.render(context)

    custom_signup_message = None
    if event.show_custom_signup_message and request.GET.get('signup', False):
        template = Template(event.custom_signup_message)
        custom_signup_message = template.render(context)

    custom_change_message = None
    if event.show_custom_change_message and request.GET.get('change', False):
        template = Template(event.custom_change_message)
        custom_change_message = template.render(context)

    context['custom_status_page'] = custom_status_page
    context['custom_signup_message'] = custom_signup_message
    context['custom_change_message'] = custom_change_message

    context['show_signup_message'] = request.GET.get('signup', False)
    context['show_change_message'] = request.GET.get('change', False)

    return render(request,
                  'eventportal/status.html',
                  context)
