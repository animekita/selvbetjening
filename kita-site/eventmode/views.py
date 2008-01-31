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

from events.models import Event, Attend
from eventmode.forms import CheckinForm
from accounting.forms import PaymentForm
from accounting.models import MembershipState

@permission_required('events.change_attend')
def event_checkin(request, event_id, template_name='eventmode/checkin.html'):
    
    event = shortcuts.get_object_or_404(Event, id=event_id)
    
    return render_to_response(template_name,
                              {'attendees' : event.get_attendees(), 'event' : event},
                              context_instance=RequestContext(request))

@permission_required('events.change_attend')
def event_usercheckin(request, event_id, user_id, template_name='eventmode/usercheckin.html'):
    
    attend = shortcuts.get_object_or_404(Attend, event=event_id, user=user_id)
    
    membershipState = attend.user.get_profile().get_membership_state()
    if membershipState == MembershipState.INACTIVE or membershipState == MembershipState.PASSIVE:
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