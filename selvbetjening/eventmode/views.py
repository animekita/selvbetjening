from datetime import datetime

from django import shortcuts
from django.shortcuts import render_to_response
from django.conf import settings
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404

from selvbetjening.events.models import Event, Attend, Option
from selvbetjening.accounting.forms import PaymentForm
from selvbetjening.accounting.models import MembershipState
from selvbetjening.core import logger
from selvbetjening.core.decorators import log_access

from forms import CheckinForm, EventmodeAccessForm
from decorators import eventmode_required

@permission_required('events.change_attend')
@log_access
def event_checkin(request, event_id, template_name='eventmode/checkin.html'):

    event = shortcuts.get_object_or_404(Event, id=event_id)

    return render_to_response(template_name,
                              {'attendees' : event.get_attendees(), 'event' : event},
                              context_instance=RequestContext(request))

@permission_required('events.change_attend')
@log_access
def event_usercheckin(request, event_id, user_id, template_name='eventmode/usercheckin.html'):

    attend = shortcuts.get_object_or_404(Attend, event=event_id, user=user_id)

    membershipState = attend.user.get_profile().get_membership_state()

    if membershipState == MembershipState.CONDITIONAL_ACTIVE:
        if attend.user.get_profile().member_since().date() == datetime.today().date():
            membershipState = MembershipState.ACTIVE

    if membershipState == MembershipState.INACTIVE or membershipState == MembershipState.PASSIVE or membershipState == MembershipState.CONDITIONAL_ACTIVE:
        needsToPay = True
        if request.method == 'POST':
            form = PaymentForm(request.POST, user=attend.user)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('eventmode_usercheckin', kwargs={'event_id':event_id, 'user_id':user_id}))
        else:
            form = PaymentForm(user=attend.user)
    else:
        needsToPay = False
        if request.method == 'POST':
            form = CheckinForm(request.POST)
            if form.is_valid():
                attend.has_attended = True
                attend.save()
                return HttpResponseRedirect(reverse('eventmode_checkin', kwargs={'event_id':event_id}))
        else:
            form = CheckinForm()

    return render_to_response(template_name,
                              {'user' : attend.user, 'event' : attend.event, 'attend' : attend,
                               'form' : form, 'needs_to_pay' : needsToPay},
                              context_instance=RequestContext(request))

@permission_required('events.change_attend')
@log_access
def event_options(request, event_id, template_name='eventmode/options.html'):

    event = get_object_or_404(Event, id=event_id)

    return render_to_response(template_name,
                              {'event' : event, 'optiongroups' : event.optiongroup_set.all()},
                              context_instance=RequestContext(request))

@permission_required('events.change_attend')
@log_access
def event_options_detail(request, event_id, option_id,
                             template_name='eventmode/options_detail.html'):

    option = get_object_or_404(Option, id=option_id)

    return render_to_response(template_name,
                              {'event' : option.group.event, 'option' : option,
                               'users' : option.users.all()},
                              context_instance=RequestContext(request))

@permission_required('events.change_attend')
@log_access
def event_list(request, template_name='eventmode/list.html'):
    return render_to_response(template_name, {'events' : Event.objects.all()},
                              context_instance=RequestContext(request))

@permission_required('events.change_attend')
@log_access
def event_statistics(request, event_id, template_name='eventmode/statistics.html'):
    event = get_object_or_404(Event, id=event_id)

    checkedin_precentage = 0
    if event.attendees_count > 0:
        checkedin_precentage = 100 * float(event.checkedin_count) / float(event.attendees_count)

    new = 0
    new_checkedin = 0
    for attendee in event.attendees:
        if attendee.is_new:
            new += 1

            if attendee.has_attended:
                new_checkedin += 1

    new_checkedin_precentage = 0
    if event.checkedin_count > 0:
        new_checkedin_precentage = 100 * float(new_checkedin) / float(event.checkedin_count)

    new_precentage = 0
    if event.attendees_count > 0:
        new_precentage = 100 * float(new) / float(event.attendees_count)

    return render_to_response(template_name,
                              {'event' : event,
                               'checkin_precentage' : checkedin_precentage,
                               'new_attendees' : new,
                               'new_checkedin' : new_checkedin,
                               'new_attendees_precentage' : new_precentage,
                               'new_checkedin_precentage' : new_checkedin_precentage},
                              context_instance=RequestContext(request))

def activate_mode(request, template_name='eventmode/activate_mode.html',
                  form_class=EventmodeAccessForm, success_page='home'):

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            request.eventmode.activate(form.cleaned_data['passphrase'])
            logger.info(request, 'client activated event-mode for event %s',
                        request.eventmode.get_model().event.id)
            return HttpResponseRedirect(reverse(success_page))
    else:
        form = form_class()

    return render_to_response(template_name,
                              {'form' : form},
                              context_instance=RequestContext(request))

def deactivate_mode(request):
    request.eventmode.deactivate()

    return HttpResponseRedirect(reverse('home'))

def info(request, template_name='eventmode/info.html'):
    return render_to_response(template_name, {},
                              context_instance=RequestContext(request))
