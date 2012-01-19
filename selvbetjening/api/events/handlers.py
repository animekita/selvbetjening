from django.contrib.auth.models import User
from django.contrib.admin.views.main import ChangeList

from piston.handler import BaseHandler

from selvbetjening.core.events.models import Attend, Invoice

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
            class Anon(object):
                ordering = None
                
                def queryset(self, request):
                    return base
                
            changelist = ChangeList(request, Attend, [], None, None, None, ('user__username',), False, 100, False, Anon())
            
            return base.all()
    
    