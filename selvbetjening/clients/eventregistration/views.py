# coding=UTF-8

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.template import Context, Template

from selvbetjening.data.logging import logger
from selvbetjening.data.invoice.models import Invoice
from selvbetjening.data.events.models import Event, Attend
from selvbetjening.data.events.decorators import \
     event_registration_open_required, \
     event_registration_allowed_required, \
     event_attendance_required
from selvbetjening.data.membership.forms import MembershipForm
from selvbetjening.data.membership.membership_controller import MembershipController

from forms import SignupForm, SignoffForm, OptionForms

def list_events(request, template_name='eventregistration/list.html'):
    ''' Show list of events. '''
    return render_to_response(template_name,
                              { 'events' : Event.objects.order_by('-startdate') },
                              context_instance=RequestContext(request))

def view(request, event_id, template_name='eventregistration/view.html'):
    event = get_object_or_404(Event, id=event_id)

    return render_to_response(template_name,
                              {'event' : event,   
                               'userIsSignedup' : event.is_attendee(request.user),
                               'attendees' : event.attendees},
                               context_instance=RequestContext(request))

@login_required
@event_registration_open_required
@event_registration_allowed_required
def signup(request, event_id,
           template_name='eventregistration/signup.html',
           template_cant_signup='eventregistration/cantsignup.html',
           template_registration_confirmation='eventregistration/registration_confirmation.html',
           form_class=SignupForm,
           form_options_class=OptionForms,
           success_page='eventregistration_view'):
    ''' Let a user sign up to the event. '''

    event = get_object_or_404(Event, id=event_id)

    if event.is_attendee(request.user):
        return render_to_response(template_cant_signup,
                                  {'event' : event},
                                  context_instance=RequestContext(request))

    if request.method == 'POST':
        form = form_class(request.POST)
        optionforms = form_options_class(event, request.POST)
        membershipform = MembershipForm(request.POST, user=request.user, event=event)
        
        if form.is_valid() and optionforms.is_valid() and membershipform.is_valid():
            logger.info(request, 'client signed user_id %s up to event_id %s' % (request.user.id, event.id))
            
            attendee = event.add_attendee(request.user)
            optionforms.save(attendee=attendee)
            
            membershipform.save(invoice=attendee.invoice)
            
            if event.show_registration_confirmation:
                template = Template(event.registration_confirmation)
                context = Context({'invoice_rev' : invoice_revision,
                                   'event' : event,
                                   'user' : attendee.user,})
                registration_confirmation = template.render(context)
                
                return render_to_response(template_registration_confirmation,
                                          {'registration_confirmation' : registration_confirmation,
                                           'event' : event},
                                          context_instance=RequestContext(request))
            
            else:
                request.user.message_set.create(message=_(u'You are now signed up to the event.'))
                return HttpResponseRedirect(reverse(success_page, kwargs={'event_id':event.id}))
    else:
        form = form_class()
        optionforms = form_options_class(event)
        membershipform = MembershipForm(user=request.user, event=event)

    return render_to_response(template_name,
                              {'event' : event,
                               'form' : form,
                               'optionforms' : optionforms,
                               'membershipform' : membershipform},
                              context_instance=RequestContext(request))

@login_required
@event_registration_open_required
@event_attendance_required
def signoff(request, event_id,
           template_name='eventregistration/signoff.html',
           success_page='eventregistration_view',
           form_class=SignoffForm):
    '''
    Let a user remove herself from an event.

    '''

    event = get_object_or_404(Event, id=event_id)
    attendee = Attend.objects.get(user=request.user, event=event)

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            logger.info(request, 'client signed user_id %s off event_id %s' % (request.user.id, event.id))
            
            event.remove_attendee(attendee.user)
            MembershipController.cancel_membership(attendee.user, attendee.invoice)
            
            request.user.message_set.create(message=_(u'You are now removed from the event.'))
            return HttpResponseRedirect(reverse(success_page, kwargs={'event_id':event.id}))
    else:
        form = form_class()

    return render_to_response(template_name, {'event' : event, 'form' : form}, context_instance=RequestContext(request))

@login_required
@event_registration_open_required
@event_attendance_required
def change_options(request, event_id, form=OptionForms,
                   success_page='eventregistration_view',
                   template_name='eventregistration/change_options.html',
                   template_change_confirmation='eventregistration/change_confirmation.html'):
    event = get_object_or_404(Event, id=event_id)
    attendee = Attend.objects.get(user=request.user, event=event)
    
    if request.method == 'POST':
        form = OptionForms(event, request.POST, attendee=attendee)
        if form.is_valid():
            form.save()
            
            if event.show_change_confirmation:
                template = Template(event.change_confirmation)
                context = Context({'invoice_rev' :  attendee.invoice.latest_revision,
                                   'event' : event,
                                   'user' : attendee.user,})
                change_confirmation = template.render(context)
                
                return render_to_response(template_change_confirmation,
                                          {'change_confirmation' : change_confirmation,
                                           'event' : event},
                                          context_instance=RequestContext(request))
            else:
                return HttpResponseRedirect(reverse(success_page, kwargs={'event_id':event.id}))
    else:
        form = OptionForms(event, attendee=attendee)

    return render_to_response(template_name,
                              {'optionforms' : form, 'event' : event },
                              context_instance=RequestContext(request))


