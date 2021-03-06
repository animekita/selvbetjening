from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import int_to_base36, urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.contrib.auth.forms import PasswordResetForm as BasePasswordResetForm, \
    SetPasswordForm as BaseSetPasswordForm

from selvbetjening.frontend.utilities.forms import S2Fieldset, S2FormHelper, S2Layout, S2Submit


class AuthenticationForm(BaseAuthenticationForm):
    helper = S2FormHelper()

    helper.add_layout(S2Layout(
        S2Fieldset(None, 'username', 'password')
    ))

    helper.add_input(
        S2Submit('submit_login', _('Log in'))
    )


class SetPasswordForm(BaseSetPasswordForm):

    layout = S2Layout(S2Fieldset(None, 'new_password1', 'new_password2'))

    helper = S2FormHelper()
    helper.add_layout(layout)
    helper.form_tag = False
    helper.add_input(S2Submit(_(u'Choose Password'), _(u'Choose Password')))


class PasswordResetForm(BasePasswordResetForm):

    layout = S2Layout(S2Fieldset(None, 'email'))

    helper = S2FormHelper()
    helper.add_layout(layout)
    helper.add_input(S2Submit(_('Recover Account'), _('Recover Account')))

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None):

        """
        Copy from BasePasswordResetForm

        Overwrites the send e-mail function to use the system e-mail queue,
        protects against smtp failures
        """

        from selvbetjening.core.mail import send_mail

        UserModel = get_user_model()
        email = self.cleaned_data["email"]
        active_users = UserModel._default_manager.filter(
            email__iexact=email, is_active=True)

        for user in active_users:
            # Make sure that no email is sent to a user that actually has
            # a password marked as unusable
            if not user.has_usable_password():
                continue
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            subject = loader.render_to_string(subject_template_name, c)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            email = loader.render_to_string(email_template_name, c)
            send_mail(subject,
                      email,
                      from_email if from_email is not None else settings.DEFAULT_FROM_EMAIL,
                      [user.email],
                      internal_sender_id='frontend.passwordreset')

