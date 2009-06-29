from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from models import Event

@staff_member_required
def event_statistics(request, event_id, template_name='admin/events/event/statistics.html'):
    event = get_object_or_404(Event, id=event_id)

    checkedin_precentage = 0
    if event.attendees_count > 0:
        checkedin_precentage = 100 * float(event.checkedin_count) / float(event.attendees_count)

    new = 0
    new_checkedin = 0
    for attendee in event.attendees:
        if attendee.is_new():
            new += 1

            if attendee.has_attended:
                new_checkedin += 1

    new_checkedin_precentage = 0
    if event.checkedin_count > 0:
        new_checkedin_precentage = 100 * float(new_checkedin) / float(event.checkedin_count)

    new_precentage = 0
    if event.attendees_count > 0:
        new_precentage = 100 * float(new) / float(event.attendees_count)

    return render_to_response(template_name,
                              {'event' : event,
                               'checkin_precentage' : checkedin_precentage,
                               'new_attendees' : new,
                               'new_checkedin' : new_checkedin,
                               'new_attendees_precentage' : new_precentage,
                               'new_checkedin_precentage' : new_checkedin_precentage},
                              context_instance=RequestContext(request))