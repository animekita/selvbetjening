from django.utils.translation import ugettext as _
from django import forms

from selvbetjening.core.forms import AcceptForm

from models import Eventmode

class CheckinForm(AcceptForm):
    def label(self):
        return _(u"This user has participated in the event")

    def error(self):
        return _(u"You must confirm his participation.")

class EventmodeAccessForm(forms.Form):
    passphrase = forms.CharField(_('Passphrase'))

    def clean_passphrase(self):
        if Eventmode.objects.check_passphrase(self.cleaned_data.get('passphrase', '')):
            return self.cleaned_data.get('passphrase', '')
        else:
            raise forms.ValidationError(_('Passphrase incorrect.'))
