from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from uni_form.helpers import FormHelper, Submit, Layout, Row, HTML

from selvbetjening.viewbase.forms.helpers import InlineFieldset

class AccessForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')

    layout = Layout(InlineFieldset(_(u"Member Access"),
                                   'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'))

    helper = FormHelper()

    submit = Submit(_('Update Access'), _('Update Access'))
    helper.add_input(submit)
    helper.use_csrf_protection = True
    helper.add_layout(layout)