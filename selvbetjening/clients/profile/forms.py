from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import PasswordChangeForm

from uni_form.helpers import FormHelper, Submit, Fieldset, Layout

class LoginForm(AuthenticationForm):
    helper = FormHelper()

    submit = Submit(_('Sign in'), _('Sign in'))
    helper.add_input(submit)
    helper.use_csrf_protection = True

class ChangePasswordForm(PasswordChangeForm):
    helper = FormHelper()

    submit = Submit(_('Change password'), _('Change password'))
    helper.add_input(submit)
    helper.use_csrf_protection = True