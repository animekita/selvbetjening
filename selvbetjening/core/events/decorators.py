from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response

from models import Event

def get_event_from_id(view_func):
    def lookup_event_id(request, event_id, *args, **kwargs):
        event = get_object_or_404(Event, id=event_id)

        return view_func(request, event, *args, **kwargs)

    return lookup_event_id


def event_registration_open_required_ext(template_name=None):

    def _view_func(view_func):

        def check_event_registration(request, event, *args, **kwargs):
            if event.is_registration_open():
                return view_func(request, event, *args, **kwargs)
            else:
                return render_to_response(template_name if template_name is not None else 'events/signup_closed.html',
                                          {'event': event},
                                          context_instance=RequestContext(request))

        return check_event_registration

    return _view_func


event_registration_open_required = event_registration_open_required_ext()


def event_registration_allowed_required(view_func):
    def check_event_registration(request, event, *args, **kwargs):
        if event.is_registration_allowed():
            return view_func(request, event, *args, **kwargs)
        else:
            return render_to_response('events/signup_disallowed.html',
                                      {'event' : event},
                                      context_instance=RequestContext(request))

    return check_event_registration

def event_attendance_required(view_func):
    def check_event_attendance(request, event, *args, **kwargs):
        if event.is_attendee(request.user):
            return view_func(request, event, *args, **kwargs)
        else:
            return render_to_response('events/requires_attendance.html',
                                      {'event' : event},
                                      context_instance=RequestContext(request))

    return check_event_attendance