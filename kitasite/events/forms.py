# coding=UTF-8

from django.utils.translation import ugettext as _

from core.forms import AcceptForm

class SignupForm(AcceptForm):

    def label(self):
        return _(u"I have read and accept the above described terms")

    def error(self):
        return _(u"You must accept to participate in the event")    
    
class SignoffForm(AcceptForm):
    def label(self):
        return _(u"Yes, remove me from the event")
    
    def error(self):
        return _(u"You must accept to remove your participation in the event")