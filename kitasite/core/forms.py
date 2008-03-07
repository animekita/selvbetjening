from django import newforms as forms
from django.utils.translation import ugettext as _

class AcceptForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(AcceptForm, self).__init__(*args, **kwargs)
        
        self.fields['confirm'] = forms.BooleanField(widget=forms.CheckboxInput(), 
                             label=self.label())
    
    def label(self):
        return _(u"I have read and accept the above described terms")

    def error(self):
        return _(u"You must accept to participate in the event")
    
    def clean_confirm(self):
        if self.cleaned_data.get('confirm', False):
            return self.cleaned_data['confirm']
        raise forms.ValidationError(self.error())

    def save(self):
        pass
