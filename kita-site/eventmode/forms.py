from django.utils.translation import ugettext as _

from core.forms import AcceptForm

class CheckinForm(AcceptForm):
    def label(self):
        return _(u"This user has participated in the event")
    
    def error(self):
        return _(u"You must confirm his participation.")
