
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.contrib.auth.forms import PasswordResetForm as BasePasswordResetForm, \
    SetPasswordForm as BaseSetPasswordForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout

from selvbetjening.frontend.base.forms import SFieldset


class AuthenticationForm(BaseAuthenticationForm):
    helper = FormHelper()

    helper.add_layout(Layout(
        SFieldset('', 'username', 'password')
    ))

    helper.add_input(
        Submit('submit_login', _('Log-in'))
    )


class SetPasswordForm(BaseSetPasswordForm):

    helper = FormHelper()
    helper.form_tag = False
    helper.add_input(Submit(_(u'Choose Password'), _(u'Choose Password')))


class PasswordResetForm(BasePasswordResetForm):

    helper = FormHelper()
    helper.form_tag = False
    helper.add_input(Submit(_('Recover Account'), _('Recover Account')))