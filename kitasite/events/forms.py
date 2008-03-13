# coding=UTF-8

from django.utils.translation import ugettext as _
from django import newforms as forms 

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

class OptionsForm(forms.Form):
    
    def __init__(self, user, event, *args, **kwargs):
        self.user = user
        self.event = event        
        
        kwargs['initial'] = {}
        for option in user.option_set.all():
            kwargs['initial'][self._get_id(option)] = True
        
        super(OptionsForm, self).__init__(*args, **kwargs)
        
        self.options = event.option_set.all().order_by('order')
        for option in self.options:
            self.fields[self._get_id(option)] = forms.BooleanField(label=option.description, 
                                                                         required=False)

    def save(self):
        if not hasattr(self, 'cleaned_data'):
            return 
        
        for option in self.options:
            if self.cleaned_data.get(self._get_id(option), False):
                # option selected
                if not self.initial.get(self._get_id(option), False):
                    # option where not selected before
                    option.users.add(self.user)
            else:
                # option not selected
                if self.initial.get(self._get_id(option), False):
                    # option where selected before
                    option.users.remove(self.user)
    
    @staticmethod
    def _get_id(option):
        return 'option_' + str(option.pk)
    