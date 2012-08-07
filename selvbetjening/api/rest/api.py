from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie import fields, constants


from django.contrib.auth.models import User

from selvbetjening.core.events.models import Attend, Event, Selection, Option, OptionGroup, SubOption

class SubOptionResource(ModelResource):

    class Meta:
        authorization = Authorization()
        queryset = SubOption.objects.all()
        resource_name = 'suboption'

        fields = ('name', 'price')

class OptionResource(ModelResource):

    suboptions = fields.ToManyField(SubOptionResource, 'suboption_set', full=True)

    class Meta:
        authorization = Authorization()
        queryset = Option.objects.all()
        resource_name = 'option'

        fields = ('name', 'description', 'freeze_time', 'maximum_attendees', 'price', 'order')

class OptionGroupResource(ModelResource):

    options = fields.ToManyField(OptionResource, 'option_set', full=True)

    class Meta:
        authorization = Authorization()
        queryset = OptionGroup.objects.all()
        resource_name = 'optiongroup'

        fields = ('name', 'description', 'minimum_selected', 'maximum_selected', 'maximum_attendees', 'freeze_time', 'order', 'package_solution', 'package_price', 'lock_selections_on_acceptance')

class EventResource(ModelResource):

    attendee_count = fields.IntegerField(readonly=True)
    option_groups = fields.ToManyField(OptionGroupResource, 'optiongroup_set', full=True)

    class Meta:
        queryset = Event.objects.all()
        resource_name = 'event'
        fields = ['id', 'title', 'startdate', 'enddate']

        authorization = Authorization()

    def dehydrate_attendee_count(self, bundle):
        return bundle.obj.attendees.count()

class UserResource(ModelResource):

    name = fields.CharField(readonly=True)

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username', 'first_name', 'last_name', 'email']

        authorization = Authorization()

    def dehydrate_name(self, bundle):
        return bundle.obj.get_full_name()

class SelectionResource(ModelResource):

    option = fields.ForeignKey(OptionResource, 'option')
    sub_option = fields.ForeignKey(SubOptionResource, 'suboption', null=True)

    attendee = fields.ToOneField('selvbetjening.api.rest.api.AttendeeResource', 'attendee')

    class Meta:
        authorization = Authorization()
        queryset = Selection.objects.all()

class AttendeeResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user', full=True)
    event = fields.ForeignKey(EventResource, 'event')
    selections = fields.ToManyField(SelectionResource, 'selection_set', related_name='attendee', full=True)

    class Meta:
        authorization = Authorization()

        queryset = Attend.objects.all()
        resource_name = 'attendee'

        filtering = {
            'event' : constants.ALL
        }

