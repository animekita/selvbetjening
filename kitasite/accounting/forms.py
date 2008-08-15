from datetime import datetime

from django import forms
from django.core.validators import alnum_re
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from models import MembershipState, Payment

class PaymentForm(forms.Form):

    TYPE_CHOICES = (
        ('FULL',_('Full subscription')),
        ('FRATE',_('First rate')),
        ('SRATE',_('Second rate')),
        )

    type = forms.CharField(max_length=5, label=_('Payment type'))

    def __init__(self, *args, **kwargs):
        self.user = kwargs['user']
        self.state = Payment.objects.get_membership_state(self.user)

        del(kwargs['user'])
        super(PaymentForm, self).__init__(*args, **kwargs)

        self.fields['type'].choices = self.get_choices()

    def clean_type(self):
        if self.cleaned_data['type'] in [choice[0] for choice in self.get_choices()]:
            return self.cleaned_data['type']

        raise forms.ValidationError(_("Payment type not valid"))

    def get_choices(self):
        if self.state == MembershipState.CONDITIONAL_ACTIVE:
            return self.TYPE_CHOICES[2:]
        elif self.state == MembershipState.INACTIVE or self.state == MembershipState.PASSIVE:
            return self.TYPE_CHOICES[0:2]
        else:
            return ()

    def save(self):
        self.user.payment_set.create(type=self.cleaned_data['type'], timestamp=datetime.now())

class PaymentsIntervalForm(forms.Form):

    startdate = forms.DateField(
        input_formats=('%d/%m/%Y', '%d/%m/%y', '%d.%m.%Y', '%d.%m.%y', '%d-%m-%Y', '%d-%m-%y'))
    enddate = forms.DateField(
        input_formats=('%d/%m/%Y', '%d/%m/%y', '%d.%m.%Y', '%d.%m.%y', '%d-%m-%Y', '%d-%m-%y'))

