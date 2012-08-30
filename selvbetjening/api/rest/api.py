from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie import fields, constants

from django.contrib.auth.models import User

from selvbetjening.core.events.models import Attend, Event, Selection, \
    Option, OptionGroup, SubOption, Invoice, Payment, AttendeeComment

class DjangoAuthentication(object):
    def is_authenticated(self, request, **kwargs):
        return request.user.is_authenticated()

    def get_identifier(self, request):
        return request.user.username

class AdminAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        return request.user.is_authenticated() and request.user.is_superuser

class SubOptionResource(ModelResource):

    class Meta:
        authentication = DjangoAuthentication()
        authorization = AdminAuthorization()

        queryset = SubOption.objects.all()
        resource_name = 'suboption'

        fields = ('name', 'price')

        always_return_data = True

class OptionResource(ModelResource):

    suboptions = fields.ToManyField(SubOptionResource, 'suboption_set', full=True)

    class Meta:
        authentication = DjangoAuthentication()
        authorization = AdminAuthorization()

        queryset = Option.objects.all()
        resource_name = 'option'

        fields = ('name', 'description', 'freeze_time', 'maximum_attendees', 'price', 'order')

        always_return_data = True

class OptionGroupResource(ModelResource):

    options = fields.ToManyField(OptionResource, 'option_set', full=True)

    class Meta:
        authentication = DjangoAuthentication()
        authorization = AdminAuthorization()

        queryset = OptionGroup.objects.all()
        resource_name = 'optiongroup'

        fields = ('name', 'description', 'minimum_selected', 'maximum_selected', 'maximum_attendees', 'freeze_time', 'order', 'package_solution', 'package_price', 'lock_selections_on_acceptance')

        always_return_data = True

class EventResource(ModelResource):

    attendee_count = fields.IntegerField(readonly=True)
    option_groups = fields.ToManyField(OptionGroupResource, 'optiongroup_set', full=True)

    class Meta:
        authentication = DjangoAuthentication()
        authorization = AdminAuthorization()

        queryset = Event.objects.all().select_related().prefetch_related('optiongroup_set').prefetch_related('optiongroup_set__option_set').prefetch_related('optiongroup_set__option_set__suboption_set')
        resource_name = 'event'
        fields = ['id', 'title', 'startdate', 'enddate']

        always_return_data = True

    def dehydrate_attendee_count(self, bundle):
        return bundle.obj.attendees.count()

class UserResource(ModelResource):

    name = fields.CharField(readonly=True)

    class Meta:
        authentication = DjangoAuthentication()
        authorization = AdminAuthorization()

        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username', 'first_name', 'last_name', 'email']

        always_return_data = True

    def dehydrate_name(self, bundle):
        return bundle.obj.get_full_name()

class SelectionResource(ModelResource):

    option = fields.ForeignKey(OptionResource, 'option')
    sub_option = fields.ForeignKey(SubOptionResource, 'suboption', null=True)

    attendee = fields.ToOneField('selvbetjening.api.rest.api.AttendeeResource', 'attendee')

    class Meta:
        authentication = DjangoAuthentication()
        authorization = AdminAuthorization()

        queryset = Selection.objects.all()

        filtering = {
            'attendee': constants.ALL
        }

        always_return_data = True

class InvoiceResource(ModelResource):

    user = fields.ToOneField(UserResource, 'user', full=False)

    amount_total = fields.IntegerField(readonly=True)
    amount_paid = fields.IntegerField(readonly=True)

    class Meta:
        authentication = DjangoAuthentication()
        authorization = AdminAuthorization()

        queryset = Invoice.objects.all()
        resource_name = 'invoice'

        fields = [None]

        always_return_data = True

    def dehydrate_amount_total(self, bundle):
        return bundle.obj.total_price

    def dehydrate_amount_paid(self, bundle):
        return bundle.obj.paid

class PaymentResource(ModelResource):

    invoice = fields.ToOneField(InvoiceResource, 'invoice')

    class Meta:
        authentication = DjangoAuthentication()
        authorization = AdminAuthorization()

        queryset = Payment.objects.all()
        resource_name = 'payment'

        always_return_data = True

class AttendeeResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user', full=True, readonly=True)
    event = fields.ForeignKey(EventResource, 'event', readonly=True)
    invoice = fields.ForeignKey(InvoiceResource, 'invoice', full=True, readonly=True)

    class Meta:
        authentication = DjangoAuthentication()
        authorization = AdminAuthorization()

        queryset = Attend.objects.all().select_related().prefetch_related('invoice__payment_set').prefetch_related('invoice__latest').prefetch_related('invoice__latest__line_set')
        resource_name = 'attendee'

        filtering = {
            'event' : constants.ALL
        }

        always_return_data = True

class AttendeeCommentResource(ModelResource):

    attendee = fields.ForeignKey(AttendeeResource, 'attendee')

    class Meta:
        authentication = DjangoAuthentication()
        authorization = AdminAuthorization()

        queryset = AttendeeComment.objects.all()
        resource_name = 'attendeecomment'

        filtering = {
            'attendee' : constants.ALL
        }

        always_return_data = True

