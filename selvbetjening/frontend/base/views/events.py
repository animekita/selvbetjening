# coding=UTF-8

from django.shortcuts import render
from django.template import Context, Template

from selvbetjening.core.events.options.dynamic_selections import SCOPE, dynamic_selections
from selvbetjening.core.events.models import Attend


def generic_event_status(request,
                         event,
                         template_name,
                         extra_context=None):

    if extra_context is None:
        extra_context = {}

    attendee = Attend.objects.get(user=request.user, event=event)

    context = {
        'event': event,
        'user': attendee.user,
        'attendee': attendee,
        'invoice': dynamic_selections(SCOPE.VIEW_USER_INVOICE, attendee)
    }

    context = Context(context)

    # status text

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

    context['custom_status_page'] = custom_status_page
    context['custom_signup_message'] = custom_signup_message
    context['custom_change_message'] = custom_change_message

    context['show_signup_message'] = request.GET.get('signup', False)
    context['show_change_message'] = request.GET.get('change', False)

    context.update(extra_context)

    return render(request,
                  template_name,
                  context)