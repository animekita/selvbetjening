from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response

from models import Event

def event_registration_open_required(view_func):
    def check_event_registration(request, event_id, *args, **kwargs):
        event = get_object_or_404(Event, id=event_id)

        if event.is_registration_open():
            return view_func(request, event_id, *args, **kwargs)
        else:
            return render_to_response('events/signup_closed.html',
                                      {'event' : event},
                                      context_instance=RequestContext(request))

    return check_event_registration

def event_registration_allowed_required(view_func):
    def check_event_registration(request, event_id, *args, **kwargs):
        event = get_object_or_404(Event, id=event_id)

        if event.is_registration_allowed():
            return view_func(request, event_id, *args, **kwargs)
        else:
            return render_to_response('events/signup_disallowed.html',
                                      {'event' : event},
                                      context_instance=RequestContext(request))

    return check_event_registration

def event_attendance_required(view_func):
    def check_event_attendance(request, event_id, *args, **kwargs):
        event = get_object_or_404(Event, id=event_id)

        if event.is_attendee(request.user):
            return view_func(request, event_id, *args, **kwargs)
        else:
            return render_to_response('events/requires_attendance.html',
                                      {'event' : event},
                                      context_instance=RequestContext(request))

    return check_event_attendance