from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response

from selvbetjening.core.events.models import Event, Attend, suspend_price_updates, resume_price_updates

__ALL__ = ('get_event_from_id',
           'event_registration_open_required_ext',
           'event_registration_allowed_required',
           'event_attendance_required',
           'suspend_automatic_attendee_price_updates')


def get_event_from_id(view_func):
    def lookup_event_pk(request, event_pk, *args, **kwargs):
        event = get_object_or_404(Event, id=event_pk)

        return view_func(request, event, *args, **kwargs)

    return lookup_event_pk


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
        if Attend.objects.can_register_to_event(event):
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


def suspend_automatic_attendee_price_updates(func):
    def _disable_updates(*args, **kw):
        try:
            suspend_price_updates()

            res = func(*args, **kw)
            return res
        except:
            raise
        finally:
            resume_price_updates()

    return _disable_updates
