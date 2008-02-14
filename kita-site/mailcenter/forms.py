import datetime

from django import newforms as forms
from django.core.validators import alnum_re
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from mailcenter.models import Mail

class CreateMailForm(forms.Form):
    def is_valid(self):
        return True

class SendPreviewEmailForm(forms.Form):
    email = forms.EmailField()
    
class EditMailForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(EditMailForm, self).__init__(*args, **kwargs)
        self.instance.date_created = datetime.date.today()
        
    class Meta:
        layout = ((_('e-mail'), (('subject', {'title' : True, 'display' : 'wide'}), ('body', {'display':'wide'}))),
              )
        model = Mail
        fields = ('subject', 'body')