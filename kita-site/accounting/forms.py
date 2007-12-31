from datetime import datetime

from django import newforms as forms
from django.core.validators import alnum_re
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from models import MembershipState
import models

class PaymentForm(forms.Form):
    
    TYPE_CHOICES = (
        ('FULL',_('Full subscription')),
        ('FRATE',_('First rate')),
        ('SRATE',_('Second rate')),
        )
    
    type = forms.CharField(max_length=5, label=_('Payment type'))
    
    def __init__(self, *args, **kwargs):
        user = kwargs['user']
        del(kwargs['user'])
        super(PaymentForm, self).__init__(*args, **kwargs)
        
        self.user = user
        self.state = models.Payment.objects.get_membership_state(user)
        
        if self.state == models.MembershipState.CONDITIONAL_ACTIVE:
            self.fields['type'].choices = self.TYPE_CHOICES[2:]
        elif self.state == models.MembershipState.INACTIVE or self.state == models.MembershipState.PASSIVE:
            self.fields['type'].choices = self.TYPE_CHOICES[0:2]
        else:
            self.fields['type'].choices = ()
    
    def clean_type(self):
        if self.state == MembershipState.CONDITIONAL_ACTIVE:
            if self.cleaned_data['type'] == 'SRATE':
                return self.cleaned_data['type'] 
        elif self.state == MembershipState.INACTIVE or self.state == MembershipState.PASSIVE:
            if self.cleaned_data['type'] == 'FULL' or self.cleaned_data['type'] == 'FRATE':
                return self.cleaned_data['type']
        
        raise forms.ValidationError(_("Payment type not valid"))
    
    def save(self):
        self.user.payment_set.create(type=self.cleaned_data['type'], timestamp=datetime.now())