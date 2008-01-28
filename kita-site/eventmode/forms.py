from datetime import datetime

from django import newforms as forms
from django.core.validators import alnum_re
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from events.forms import AcceptForm

class CheckinForm(AcceptForm):
    confirm = forms.BooleanField(widget=forms.CheckboxInput(), initial=True, 
                             label=_(u"This user has participated in the event"))
