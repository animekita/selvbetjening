# coding=UTF-8

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db.models.aggregates import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import Context, Template, RequestContext
from django.utils.translation import ugettext as _
from django.contrib import messages
from core.events.dynamic_selections import dynamic_statistics

from selvbetjening.core.events.models import Event, Attend, attendes_event_source
from selvbetjening.core.events import decorators as eventdecorators
from selvbetjening.core.events.decorators import suspend_automatic_attendee_price_updates


def events_list(request,
                template_name='eventportal/list.html'):

    return render(request,
                  template_name,
                  {
                      'events': Event.objects.order_by('-startdate')
                  })


def event(request,
          event_pk,
          template_name='eventportal/event.html'):

    instance = get_object_or_404(Event, pk=event_pk)

    # Attendee stats

    attendee_stats = {}

    for item in instance.attendees.values('state').annotate(count=Count('pk')):
        attendee_stats[item['state']] = item['count']

    attendee_stats['accepted'] = attendee_stats['accepted'] + attendee_stats['attended']
    del attendee_stats['attended']

    # Options stats

    public_options = dynamic_statistics(instance)

    return render(request,
                  template_name,
                  {
                      'event': instance,
                      'is_attendee': instance.is_attendee(request.user),
                      'attendee_stats': attendee_stats,
                      'public_options': public_options
                  })


def event_attendees(request):
    return None


def event_register(request):
    return None


def event_unregister(request):
    return None


def event_status_update(request):
    return None


def event_status(request):
    return None