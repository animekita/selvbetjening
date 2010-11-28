# coding=UTF-8

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context, Template, RequestContext
from django.template.loader import get_template_from_string
from django.utils.translation import ugettext as _

from selvbetjening.data.logger import logger
from selvbetjening.data.invoice.decorators import disable_invoice_updates
from selvbetjening.data.events.models import Event, Attend
from selvbetjening.data.events import decorators as eventdecorators

from forms import SignupForm, SignoffForm, OptionForms
from processor_handlers import signup_processors, change_processors

if 'mailer' in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
    from django.core.mail import send_mail

def list_events(request, template_name='eventregistration/list.html'):
    return render_to_response(template_name,
                              { 'events' : Event.objects.order_by('-startdate') },
                              context_instance=RequestContext(request))

def event_page(request, event, template_name, extra_template_vars=None):
    template_vars = {'event' : event,
                     'is_attendee' : event.is_attendee(request.user)}

    if extra_template_vars is not None:
        template_vars.update(extra_template_vars)

    return render_to_response(template_name, template_vars,
                               context_instance=RequestContext(request))

@eventdecorators.get_event_from_id
def information(request, event,
                template_name='eventregistration/information.html'):

    return event_page(request, event, template_name)

@eventdecorators.get_event_from_id
def attendees(request, event,
              template_name='eventregistration/attendees.html'):

    return event_page(request, event, template_name,
                      {'attendees': event.attendees})

@login_required
@eventdecorators.get_event_from_id
@eventdecorators.event_registration_open_required
@eventdecorators.event_registration_allowed_required
@disable_invoice_updates
def signup(request, event,
           template_name='eventregistration/signup.html',
           form_class=SignupForm,
           form_options_class=OptionForms,
           success_page='eventregistration_status'):

    if event.is_attendee(request.user):
        return HttpResponseRedirect(
            reverse('eventregistration_status', args=[event.pk,]))

    handler = signup_processors.get_handler(request, request.user, event)

    if request.method == 'POST':
        form = form_class(request.POST)
        optionforms = form_options_class(event, request.POST)

        if form.is_valid() and optionforms.is_valid() and handler.is_valid():

            log_msg = '<user %s> registered for <event %s>' %\
                    (request.user.username, event.title)

            logger.log('eventregistration', 'event-registration', log_msg,
                       request=request, event=event)

            attendee = event.add_attendee(request.user)
            optionforms.save(attendee=attendee)

            handler.save(attendee)

            attendee.invoice.update(force=True)

            if event.email_on_signup:
                subject = event.email_subject
                context = {'event' : event,
                           'invoice_rev' : attendee.invoice.latest_revision,
                           'attendee' : attendee}

                template = get_template_from_string(event.email_body)
                message_body = template.render(Context(context))

                send_mail(subject, message_body,
                          settings.DEFAULT_FROM_EMAIL, [attendee.user.email,])

            return HttpResponseRedirect(
                reverse(success_page, kwargs={'event_id' : event.pk}) + '?signup=1')

    else:
        form = form_class()
        optionforms = form_options_class(event)

    handler_view = handler.view()

    return event_page(request, event, template_name,
                      {'form' : form,
                       'optionforms' : optionforms,
                       'signup_parts' : handler_view})

@login_required
@eventdecorators.get_event_from_id
@eventdecorators.event_registration_open_required
@eventdecorators.event_attendance_required
@disable_invoice_updates
def signoff(request, event,
            template_name='eventregistration/signoff.html',
            success_page='eventregistration_information',
            form_class=SignoffForm):

    attendee = Attend.objects.get(user=request.user, event=event)

    if request.method == 'POST':
        form = form_class(request.POST)

        if form.is_valid():

            log_msg = '<user %s> removed registration for <event %s>' %\
                    (request.user.username, event.title)

            logger.log('eventregistration', 'event-registration', log_msg,
                        request=request, event=event)

            attendee.delete()

            attendee.invoice.update(force=True)

            request.user.message_set.create(
                message=_(u'You are now removed from the event.'))

            return HttpResponseRedirect(
                reverse(success_page, kwargs={'event_id':event.id}) + '?change=1')

    else:
        form = form_class()

    return event_page(request, event, template_name, {'form' : form})

@login_required
@eventdecorators.get_event_from_id
@eventdecorators.event_registration_open_required
@eventdecorators.event_attendance_required
@disable_invoice_updates
def change_options(request, event,
                   form=OptionForms,
                   success_page='eventregistration_status',
                   template_name='eventregistration/change_options.html'):

    attendee = Attend.objects.get(user=request.user, event=event)

    handler = change_processors.get_handler(request, attendee)

    if request.method == 'POST':
        form = OptionForms(event, request.POST, attendee=attendee)

        if form.is_valid() and handler.is_valid():
            form.save()

            handler.save()

            attendee.invoice.update(force=True)

            log_msg = '<user %s> changed options for <event %s>' %\
                    (attendee.user.username, attendee.event.title)

            logger.log('eventregistration', 'event-registration', log_msg,
                       request=request, event=attendee.event)

            return HttpResponseRedirect(
                reverse(success_page, kwargs={'event_id':event.id}))

    else:
        form = OptionForms(event, attendee=attendee)

    signup_render = handler.view()

    return event_page(request, event, template_name,
                      {'optionforms' : form,
                       'signup_render' : signup_render})

@login_required
@eventdecorators.get_event_from_id
@eventdecorators.event_attendance_required
def view_invoice(request, event,
                 template_name='eventregistration/status.html'):

    attendee = Attend.objects.get(user=request.user, event=event)

    template_vars = {'invoice_rev' :  attendee.invoice.latest_revision,
                     'event' : event,
                     'user' : attendee.user,
                     'attendee': attendee}

    context = Context(template_vars)

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

    template_vars['custom_status_page'] = custom_status_page
    template_vars['custom_signup_message'] = custom_signup_message
    template_vars['custom_change_message'] = custom_change_message

    template_vars['show_signup_message'] = request.GET.get('signup', False)
    template_vars['show_change_message'] = request.GET.get('change', False)

    return event_page(request, event, template_name, template_vars)
