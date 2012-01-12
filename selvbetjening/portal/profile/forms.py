from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import PasswordChangeForm
from django import forms

from uni_form.helpers import FormHelper, Submit, Layout, HTML

from selvbetjening.viewbase.forms.helpers import InlineFieldset, Fieldset
from selvbetjening.core.members.forms import UsernameField, validate_username

from processor_handlers import extended_privacy_processors
from models import UserPrivacy

class LoginForm(AuthenticationForm):
    helper = FormHelper()

    layout = Layout(Fieldset(None, 'username', 'password'))
    submit = Submit('submit_login', _('Sign in'))

    helper.add_layout(layout)
    helper.add_input(submit)
    helper.use_csrf_protection = True
    
    def clean(self):
        """
        Overwrite clean in order to provide an more clean error message
        """
        
        try:
            return super(LoginForm, self).clean()
        except forms.ValidationError, ex:
            if self.user_cache is None:
                ex = forms.ValidationError(_(u"Please enter a correct username and password."))
            
            raise ex

class ChangePasswordForm(PasswordChangeForm):
    helper = FormHelper()

    submit = Submit(_('Change password'), _('Change password'))
    helper.add_input(submit)
    helper.use_csrf_protection = True

class ChangeUsernameForm(forms.Form):
    new_username = UsernameField()

    helper = FormHelper()

    layout = Layout(InlineFieldset(_('New username'), 'new_username'))
    submit = Submit(_('Change username'), _('Change username'))

    helper.add_layout(layout)
    helper.add_input(submit)
    helper.use_csrf_protection = True

    def clean_new_username(self):
        return validate_username(self.cleaned_data['new_username'])

class ChangePictureForm(forms.Form):
    picture = forms.ImageField(label=_(u'Picture'))

    helper = FormHelper()

    submit = Submit(_('Change picture'), _('Change picture'))
    helper.add_input(submit)
    helper.use_csrf_protection = True

class PrivacyForm(forms.ModelForm):
    html = """
    <script type="text/javascript">
    public_input = null;

    function update_toggle() {
        inputs = $('input');

        $('.privacy_settings').slideToggle();
    }

    $(window).load(function () {
        public_input = $('#id_public_profile')[0];

        $(public_input).change(function() {
            update_toggle();
        });

        if (public_input.checked == false) {
            $('.privacy_settings').hide();
        }
    });

    $
    </script>
    """

    public_profile = forms.BooleanField(label=_('Public profile'), required=False)
    public_name = forms.BooleanField(label=_('Name'), required=False)
    public_age = forms.BooleanField(label=_('Age'), required=False)
    public_sex = forms.BooleanField(label=_('Sex'), required=False)
    public_email = forms.BooleanField(label=_('Email'), required=False)
    public_phonenumber = forms.BooleanField(label=_('Phonenumber'), required=False)
    public_town = forms.BooleanField(label=_('Town'), required=False)
    public_contact = forms.BooleanField(label=_('Contact'), required=False)
    public_websites = forms.BooleanField(label=_('Websites'), required=False)
    public_join_date = forms.BooleanField(label=_('Join date'), required=False)

    def __init__(self, *args, **kwargs):
        super(PrivacyForm, self).__init__(*args, **kwargs)

        privacy = kwargs['instance']
        self.privacy_handler = extended_privacy_processors.get_handler(privacy.user)

        self.extended_options = self.privacy_handler.get_privacy_options()
        extended_fields = []

        for option in self.extended_options:
            key, name, value = option
            self.fields[key] = forms.BooleanField(label=name, required=False)
            self.initial[key] = value
            extended_fields.append(key)

        # args and kwargs is a fix for python 2.5
        fields = [_('Visible on my profile'),
                  'public_name', 'public_age', 'public_sex',
                  'public_join_date',
                  'public_email', 'public_phonenumber',
                  'public_town', 'public_contact',
                  'public_websites',] + extended_fields

        options = {'ext_class' : 'privacy_settings',
                  'help_text' : _('Select the information which is to be visible on your profile.')}

        layout = Layout(InlineFieldset(None, 'public_profile'),
                        InlineFieldset(*fields, **options),
                        HTML(self.html))

        submit = Submit(_('Update privacy settings'), _('Update privacy settings'))

        self.helper = FormHelper()
        self.helper.add_input(submit)
        self.helper.add_layout(layout)
        self.helper.use_csrf_protection = True

    def save(self, *args, **kwargs):
        super(PrivacyForm, self).save(*args, **kwargs)

        options = {}
        for option in self.extended_options:
            key, name, value = option
            options[key] = self.cleaned_data[key]

        self.privacy_handler.save_privacy_options(options)

    class Meta:
        model = UserPrivacy
        exclude = ('user',)
