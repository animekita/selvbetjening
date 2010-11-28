from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.template import Context, Template

from selvbetjening.core.invoice.decorators import disable_invoice_updates

import decorators
import forms

@decorators.event_registration_open_required
@decorators.event_registration_allowed_required
@disable_invoice_updates
def signup(request, event_id, template_name, template_cant_signup, template_registration_confirmation,
           success_page, form_class=forms.SignupForm, form_options_class=forms.OptionForms):
    ''' Let a user sign up to the event. '''

    event = get_object_or_404(Event, id=event_id)

    if event.is_attendee(request.user):
        return render_to_response(template_cant_signup,
                                  {'event' : event},
                                  context_instance=RequestContext(request))

    signup_allowed, render_functions, save_functions = \
                  handlers.signup.run_processors(request, request.user, event)

    if request.method == 'POST':
        form = form_class(request.POST)
        optionforms = form_options_class(event, request.POST)

        if form.is_valid() and optionforms.is_valid() and signup_allowed:
            logger.info(request, 'client signed user_id %s up to event_id %s' % (request.user.id, event.id))

            attendee = event.add_attendee(request.user)
            optionforms.save(attendee=attendee)

            for save_func in save_functions:
                save_func(attendee)

            attendee.invoice.update(force=True)

            if event.show_registration_confirmation:
                template = Template(event.registration_confirmation)
                context = Context({'invoice_rev' : attendee.invoice.latest_revision,
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

    # Render the signup parts
    signup_parts = ''
    for render_func in render_functions:
        signup_parts += render_func()

    return render_to_response(template_name,
                              {'event' : event,
                               'form' : form,
                               'optionforms' : optionforms,
                               'signup_parts' : signup_parts},
                              context_instance=RequestContext(request))