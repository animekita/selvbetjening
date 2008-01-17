# coding=UTF-8
from datetime import date

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from events.models import Event
from events.forms import SignupForm, SignoffForm
from accounting import models as accounting_models

TEMPLATE_NO_EVENT='events/noevent.html'
TEMPLATE_CANT_SIGNUP='events/cantsignup.html'
TEMPLATE_CANT_SIGNOFF='events/cantsignoff.html'

@login_required
def visited(request, template_name='events/visited.html'):
    """
    View all the events the currently logged in user has participated in
    """
    return render_to_response(template_name, 
                              {'events' : request.user.event_set.all() }, 
                              context_instance=RequestContext(request))

def list(request, template_name='events/list.html'):
    """
    View detailed information about an event
    """
    return render_to_response(template_name,
                              { 'events' : Event.objects.order_by('-startdate') },
                              context_instance=RequestContext(request))

def view(request, eventId=None, template_name='events/view.html'):
    """
    View event
    
    - Show signup field if user is logged in and not signedup to the event
    - If event does not exist in the database, show error page (TEMPLATE_NO_EVENT)
    """
    
    try:
        event = Event.objects.get(id=eventId)
    except ObjectDoesNotExist:
        return render_to_response(TEMPLATE_NO_EVENT, context_instance=RequestContext(request))
    
    return render_to_response(template_name, 
                              {'event' : event, 
                                'userIsSignedup' : event.signups.filter(id=request.user.id),
                                'guests' : Event.objects.get(id=event.id).get_guests()}, 
                              context_instance=RequestContext(request))

@login_required
def signup(request, 
           eventId=None, 
           template_name='events/signup.html', 
           form_class=SignupForm,
           success_page='events_view'):
    """
    Let a user sign up to the event
    
    - User must be logged in to view the page
    - Show confirmation page
    - If the user already is signed up to the event, the event hasent opened for registration
    or the event does not exist show error pages (TEMPLATE_ALREADY_SIGNEDUP, TEMPLATE_CANT_SIGNUP and TEMPLATE_NO_EVENT)
    
    """
    
    try:
        event = Event.objects.get(id=eventId)
    except ObjectDoesNotExist:
        return render_to_response(TEMPLATE_NO_EVENT, context_instance=RequestContext(request))
    
    if not event.isRegistrationOpen() or event.signups.filter(id=request.user.id):
        return render_to_response(TEMPLATE_CANT_SIGNUP, context_instance=RequestContext(request))
    
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            event.signups.add(request.user)
            request.user.message_set.create(message=_(u"You are now signed up to the event."))
            return HttpResponseRedirect(reverse(success_page, kwargs={'eventId':event.id}))
    else:
        form = form_class()
    
    # is the user underaged at the time
    is_underaged = request.user.get_profile().isUnderaged(date = event.startdate)
    
    membership_state = accounting_models.Payment.objects.get_membership_state(request.user)
    
    return render_to_response(template_name, {'event' : event, 'form' : form, 'is_underaged' : is_underaged, 'membership_state' : membership_state}, context_instance=RequestContext(request))

@login_required
def signoff(request,
           eventId=None, 
           template_name='events/signoff.html', 
           success_page='events_view',
           form_class=SignoffForm):

    event = get_object_or_404(Event, id=eventId)
    
    if not event.isRegistrationOpen() or not event.signups.filter(id=request.user.id): 
        # registratio not open or user not signed up to the event
        return render_to_response(TEMPLATE_CANT_SIGNOFF, context_instance=RequestContext(request))
    
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            event.signups.remove(request.user)
            request.user.message_set.create(message=_(u"You are now removed from the event."))
            return HttpResponseRedirect(reverse(success_page, kwargs={'eventId':event.id}))
    else:
        form = form_class()
    
    return render_to_response(template_name, {'event' : event, 'form' : form}, context_instance=RequestContext(request))   