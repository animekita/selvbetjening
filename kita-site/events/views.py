# coding=UTF-8

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from datetime import date

from events.models import Event
from events.forms import SignupForm

from django.contrib.auth.models import User

TEMPLATE_NO_EVENT='events/noevent.html'
TEMPLATE_CANT_SIGNUP='events/cantsignup.html'

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
                                'guests' : User.objects.order_by('id').filter(event__id=event.id)}, 
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
    
    @todo Requre login
    """
    
    try:
        event = Event.objects.get(id=eventId)
    except ObjectDoesNotExist:
        return render_to_response(TEMPLATE_NO_EVENT, context_instance=RequestContext(request))
    
    if not event.isRegistrationOpen():
        return render_to_response(TEMPLATE_CANT_SIGNUP, context_instance=RequestContext(request))
    
    if event.signups.filter(id=request.user.id):
        return HttpResponseRedirect(reverse(success_page, kwargs={'eventId':event.id}))
    
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            event.signups.add(request.user)
            request.user.message_set.create(message=_(u"You are now signed up to the event."))
            return HttpResponseRedirect(reverse(success_page, kwargs={'eventId':event.id}))
    else:
        form = form_class()
    
    return render_to_response(template_name, {'event' : event, 'form' : form}, context_instance=RequestContext(request))