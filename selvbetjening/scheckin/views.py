
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from selvbetjening.sadmin.decorators import superuser_required
from selvbetjening.api.rest.api import EventResource, AttendeeResource

@login_required
@superuser_required
def checkin(request, event_id):

    event_resource = EventResource()
    event = event_resource.obj_get(pk=event_id)

    bundle = event_resource.build_bundle(obj=event, request=request)
    bundle = event_resource.full_dehydrate(bundle)

    event_json = event_resource.serialize(None, bundle, 'application/json')

    attendee_resource = AttendeeResource()
    attendees = attendee_resource.obj_get_list(event=event_id)
    attendees_list = []

    for attendee in attendees:
        bundle = attendee_resource.build_bundle(obj=attendee, request=request)
        bundle = attendee_resource.full_dehydrate(bundle)
        attendees_list.append(bundle)

    attendees_json = attendee_resource.serialize(None, attendees_list, 'application/json')

    return render(request, 'scheckin/application.html', {
        'event_json': event_json,
        'attendees_json': attendees_json
    })