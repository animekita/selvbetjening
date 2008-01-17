# coding=UTF-8

"""
Forms and validation code for events.

"""


from django import newforms as forms
from django.core.validators import alnum_re
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
    
class SignupForm(forms.Form):
    
    tos = forms.BooleanField(widget=forms.CheckboxInput(), 
                             label=_(u"I have read and accept the above described terms"))
    
    def clean_tos(self):
        """
        Validates that the user accepted the Terms of Service.
        
        """
        if self.cleaned_data.get('tos', False):
            return self.cleaned_data['tos']
        raise forms.ValidationError(_(u"You must accept to participate in the event"))
    
    def save(self):
        pass

class SignoffForm(forms.Form):
    
    confirm = forms.BooleanField(widget=forms.CheckboxInput(), 
                             label=_(u"Yes, remove me from the event"))
    
    def clean_tos(self):
        """
        Validates that the user accepted the Terms of Service.
        
        """
        if self.cleaned_data.get('tos', False):
            return self.cleaned_data['tos']
        raise forms.ValidationError(_(u"You must accept to participate in the event"))
    
    def save(self):
        pass
    