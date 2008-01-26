# coding=UTF-8

"""
Forms and validation code for events.

"""


from django import newforms as forms
from django.core.validators import alnum_re
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

class AcceptForm(forms.Form):

        def clean_confirm(self):
                """
                Validates that the user accepted the Terms of Service.
                
                """
                if self.cleaned_data.get('confirm', False):
                        return self.cleaned_data['confirm']
                raise forms.ValidationError(_(u"You must accept to participate in the event"))
            
        def save(self):
                pass

class SignupForm(AcceptForm):
        confirm = forms.BooleanField(widget=forms.CheckboxInput(), 
                             label=_(u"I have read and accept the above described terms"))

class SignoffForm(AcceptForm):
        confirm = forms.BooleanField(widget=forms.CheckboxInput(), 
                             label=_(u"Yes, remove me from the event"))