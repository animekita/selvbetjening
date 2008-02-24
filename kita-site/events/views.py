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
from django.newforms import BooleanField

from events.models import Event
from events.forms import SignupForm, SignoffForm
from accounting import models as accounting_models

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
                                'userIsSignedup' : event.is_attendee(request.user),
                                'attendees' : event.get_attendees()}, 
                              context_instance=RequestContext(request))

@login_required
def signup(request, 
           eventId=None, 
           template_name='events/signup.html', 
           template_cant_signup='events/cantsignup.html',
           form_class=SignupForm,
           success_page='events_view'):
    """
    Let a user sign up to the event.
    
    """
    
    event = get_object_or_404(Event, id=eventId)
    
    if not event.is_registration_open() or event.is_attendee(request.user):
        return render_to_response(template_cant_signup, context_instance=RequestContext(request))
    
    def add_dynamic_options(form):
        for option in event.option_set.all():
            form.fields['option_' + str(option.pk)] = BooleanField(label=option.description, required=False)

    def fetch_and_store_options(form):
        for option in event.option_set.all():
            if form.cleaned_data.get('option_' + str(option.pk), False):
                option.users.add(request.user)
            
    if request.method == 'POST':
        form = form_class(request.POST)
        add_dynamic_options(form)
        if form.is_valid():
            event.add_attendee(request.user)
            fetch_and_store_options(form)
            request.user.message_set.create(message=_(u"You are now signed up to the event."))
            return HttpResponseRedirect(reverse(success_page, kwargs={'eventId':event.id}))
    else:
        form = form_class()
        add_dynamic_options(form)

    # is the user underaged at the time
    is_underaged = request.user.get_profile().isUnderaged(date = event.startdate)
    
    membership_state = accounting_models.Payment.objects.get_membership_state(request.user)
    
    return render_to_response(template_name, {'event' : event, 'form' : form, 'is_underaged' : is_underaged, 'membership_state' : membership_state}, context_instance=RequestContext(request))

@login_required
def signoff(request,
           eventId=None, 
           template_name='events/signoff.html', 
           template_cant_signoff='events/cantsignoff.html',
           success_page='events_view',
           form_class=SignoffForm):
    """
    Let a user remove herself from an event.
    
    """

    event = get_object_or_404(Event, id=eventId)
    
    if not event.is_registration_open() or not event.is_attendee(request.user): 
        # registratio not open or user not signed up to the event
        return render_to_response(template_cant_signoff, context_instance=RequestContext(request))
    
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            event.remove_attendee(request.user)
            request.user.message_set.create(message=_(u"You are now removed from the event."))
            return HttpResponseRedirect(reverse(success_page, kwargs={'eventId':event.id}))
    else:
        form = form_class()
    
    return render_to_response(template_name, {'event' : event, 'form' : form}, context_instance=RequestContext(request))   