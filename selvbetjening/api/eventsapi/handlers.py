from django.contrib.auth.models import User

from piston.handler import BaseHandler

from selvbetjening.core.events.models import Attend, Invoice
from selvbetjening.api import api_search_filter

class UserHandler(BaseHandler):
    model = User
    fields = ('username', 'first_name', 'last_name', 'email')

class InvoiceHandler(BaseHandler):
    model = Invoice
    fields = ('paid',)

    @classmethod
    def paid(cls, invoice):
        return invoice.is_paid()

class AttendeeHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Attend
    exclude = ('event',)

    def read(self, request, event_pk=None, attendee_pk=None):

        base = Attend.objects

        if event_pk is not None:
            base = base.filter(event__pk=event_pk)

        if attendee_pk is not None:
            return base.get(pk=attendee_pk)

        else:
            base = api_search_filter(request, base, Attend, ['user__username',
                                                             'user__first_name',
                                                             'user__last_name',
                                                             'user__email'])

            return base.all()

