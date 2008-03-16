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
from events.forms import SignupForm, SignoffForm, OptionsForm
from events.decorators import event_registration_open_required, event_attendance_required
from accounting import models as accounting_models
from core import logger

@login_required
def visited(request, template_name='events/visited.html'):
    """
    View all the events the currently logged-in user has participated in
    
    """
    return render_to_response(template_name, 
                              {'events' : request.user.event_set.all() }, 
                              context_instance=RequestContext(request))

def list(request, template_name='events/list.html'):
    """
    Show list of events
    
    """
    return render_to_response(template_name,
                              { 'events' : Event.objects.order_by('-startdate') },
                              context_instance=RequestContext(request))

def view(request, event_id, template_name='events/view.html'):
    
    event = get_object_or_404(Event, id=event_id)
    
    return render_to_response(template_name, 
                              {'event' : event,
                               'has_options' : (len(event.option_set.all()) > 0),
                               'userIsSignedup' : event.is_attendee(request.user),
                               'attendees' : event.get_attendees()}, 
                               context_instance=RequestContext(request))

@login_required
@event_registration_open_required
def signup(request, event_id, 
           template_name='events/signup.html', 
           template_cant_signup='events/cantsignup.html',
           form_class=SignupForm,
           success_page='events_view'):
    """
    Let a user sign up to the event.
    
    """
    
    event = get_object_or_404(Event, id=event_id)
    
    if event.is_attendee(request.user):
        return render_to_response(template_cant_signup, 
                                  {'event' : event},
                                  context_instance=RequestContext(request))
    
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
            logger.info(request, 'client signed user_id %s up to event_id %s' % (request.user.id, event.id))
            event.add_attendee(request.user)
            fetch_and_store_options(form)
            request.user.message_set.create(message=_(u"You are now signed up to the event."))
            return HttpResponseRedirect(reverse(success_page, kwargs={'event_id':event.id}))
    else:
        form = form_class()
        add_dynamic_options(form)

    # is the user underaged at the time
    is_underaged = request.user.get_profile().isUnderaged(date = event.startdate)
    
    membership_state = accounting_models.Payment.objects.get_membership_state(request.user)
    
    return render_to_response(template_name, {'event' : event, 'form' : form, 'is_underaged' : is_underaged, 'membership_state' : membership_state}, context_instance=RequestContext(request))

@login_required
@event_registration_open_required
@event_attendance_required
def signoff(request, event_id, 
           template_name='events/signoff.html', 
           success_page='events_view',
           form_class=SignoffForm):
    """
    Let a user remove herself from an event.
    
    """

    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            logger.info(request, 'client signed user_id %s off event_id %s' % (request.user.id, event.id))
            event.remove_attendee(request.user)
            request.user.message_set.create(message=_(u"You are now removed from the event."))
            return HttpResponseRedirect(reverse(success_page, kwargs={'event_id':event.id}))
    else:
        form = form_class()
    
    return render_to_response(template_name, {'event' : event, 'form' : form}, context_instance=RequestContext(request))   

@login_required
@event_registration_open_required
@event_attendance_required
def change_options(request, event_id, form=OptionsForm,
                   success_page='events_view',
                   template_name='events/change_options.html'):
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = OptionsForm(request.user, event, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(success_page, kwargs={'event_id':event.id}))
    else:
        form = OptionsForm(request.user, event)
    
    return render_to_response(template_name, 
                              {'form' : form, 'event' : event }, 
                              context_instance=RequestContext(request))
