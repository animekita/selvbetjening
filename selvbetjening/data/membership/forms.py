from datetime import datetime

from django import forms
from django.utils.translation import ugettext as _
from django.contrib.admin import widgets

from membership_controller import MembershipController

class MembershipForm(forms.Form):
    type = forms.ChoiceField(label=_('Payment type'))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.event = kwargs.pop('event', None)

        super(MembershipForm, self).__init__(*args, **kwargs)

        choices_full = MembershipController.get_membership_choices(self.user, self.event)
        choices = [(choice['id'], choice['description']) for choice in choices_full]

        self.choices = choices
        self.fields['type'].choices = choices

    def clean_type(self):
        if self.cleaned_data['type'] in [choice[0] for choice in self.choices]:
            return self.cleaned_data['type']

        raise forms.ValidationError(_("Payment type not valid"))

    def has_options(self):
        return len(self.choices) > 0    
    
    def is_valid(self):
        if self.has_options():
            return super(MembershipForm, self).is_valid()
        
        return True
    
    def save(self, invoice=None):
        if self.has_options():
            MembershipController.select_membership(self.user, self.cleaned_data['type'], event=self.event, invoice=invoice)

class PaymentsIntervalForm(forms.Form):

    startdate = forms.DateField(
        #input_formats=('%d/%m/%Y', '%d/%m/%y', '%d.%m.%Y', '%d.%m.%y', '%d-%m-%Y', '%d-%m-%y'),
        widget=widgets.AdminDateWidget())
    enddate = forms.DateField(
        #input_formats=('%d/%m/%Y', '%d/%m/%y', '%d.%m.%Y', '%d.%m.%y', '%d-%m-%Y', '%d-%m-%y'),
        widget=widgets.AdminDateWidget())

