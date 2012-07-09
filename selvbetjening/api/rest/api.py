from tastypie.resources import ModelResource

from selvbetjening.core.events.models import Attend, Invoice

class AttendeeResource(ModelResource):
    class Meta:
        queryset = Attend.objects.all()
        resource_name = 'attendee'