
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from selvbetjening.sadmin.decorators import superuser_required
from selvbetjening.api.rest.api import EventResource, AttendeeResource

@login_required
@superuser_required
def checkin(request, event_id):

    event_resource = EventResource()

    event_bundle = event_resource.build_bundle(request=request)
    event_resource.obj_get(event_bundle, pk=event_id)
    event_bundle = event_resource.full_dehydrate(event_bundle)

    event_json = event_resource.serialize(None, event_bundle, 'application/json')

    attendee_resource = AttendeeResource()
    attendee_bundle = attendee_resource.build_bundle(request=request)
    attendees = attendee_resource.obj_get_list(attendee_bundle, event=event_id)

    attendees_list = []

    for attendee in attendees:
        event_bundle = attendee_resource.build_bundle(obj=attendee, request=request)
        event_bundle = attendee_resource.full_dehydrate(event_bundle)
        attendees_list.append(event_bundle)

    attendees_json = attendee_resource.serialize(None, attendees_list, 'application/json')

    return render(request, 'scheckin/application.html', {
        'event_json': event_json,
        'attendees_json': attendees_json
    })