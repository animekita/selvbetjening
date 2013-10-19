
from django import forms
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
from django.forms.models import inlineformset_factory, BaseInlineFormSet

from selvbetjening.core.members import signals
from selvbetjening.core.members.models import UserProfile, UserWebsite
from selvbetjening.frontend.utilities.forms import *


class MinimalUserRegistrationForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ('username',)

    username = UsernameField()

    password = forms.CharField(widget=forms.PasswordInput(),
                               label=_(u"Password"),
                               required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(),
                                label=_(u"Verify password"),
                                required=True)

    def __init__(self, *args, **kwargs):
        super(MinimalUserRegistrationForm, self).__init__(*args, **kwargs)

        self.helper = S2FormHelper(horizontal=True)

        layout = S2Layout(
            S2Fieldset(None,
                       'username',
                       'password', 'password2'))

        self.helper.add_layout(layout)
        self.helper.add_input(S2SubmitUpdate() if 'instance' in kwargs else S2SubmitCreate())

    def clean_password2(self):

        if 'password' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_(u"You must type the same password each time"))

        return self.cleaned_data.get('password2', None)

    def save(self, *args, **kwargs):

        user = super(MinimalUserRegistrationForm, self).save(*args, **kwargs)

        user.set_password(self.cleaned_data['password'])
        user.is_active = True
        user.save()

        signals.user_created.send(sender=self,
                                  instance=user,
                                  clear_text_password=smart_str(self.cleaned_data['password']))

        return user


class UserRegistrationForm(MinimalUserRegistrationForm):

    class Meta:
        model = UserProfile

        widgets = {
            'dateofbirth': SplitDateWidget(),
        }

        fields = ('username', 'first_name', 'last_name', 'sex', 'dateofbirth', 'email',
                  'phonenumber', 'street', 'postalcode', 'city', 'country', 'send_me_email')

    first_name = forms.CharField(max_length=50,
                                 widget=forms.TextInput(),
                                 label=_(u'First name'),
                                 required=True)

    last_name = forms.CharField(max_length=50,
                                widget=forms.TextInput(),
                                label=_(u'Last name'),
                                required=True)

    phonenumber = forms.RegexField(label=_(u'Phonenumber'),
                                   required=False,
                                   regex=r'(\+[0-9]{2}( )?)?([0-9]{8})')

    send_me_email = forms.BooleanField(widget=forms.CheckboxInput(),
                                       label=_(u'Inform me about events and other important changes.'),
                                       initial=True,
                                       required=False)

    tos = forms.BooleanField(widget=forms.CheckboxInput(),
                             label=_(u"I allow the storage of my personal information on this site."),
                             required=True)

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)

        self.helper = S2FormHelper(horizontal=True)

        layout = S2Layout(
            S2Fieldset(None,
                       'username',
                       'password', 'password2'),
            S2Fieldset(_('Personal info'),
                       'first_name', 'last_name', 'sex', 'dateofbirth', collapse=False),
            S2Fieldset(_('Contact'),
                       'email', 'phonenumber', collapse=False),
            S2Fieldset(_('Address'),
                       'street', 'postalcode', 'city', 'country', collapse=False),
            S2Fieldset(None,
                       'send_me_email', 'tos', collapse=False))

        self.helper.add_layout(layout)
        self.helper.add_input(S2SubmitUpdate() if 'instance' in kwargs else S2SubmitCreate())


class ProfileEditForm(forms.ModelForm):

    class Meta:
        model = UserProfile

        widgets = {
            'dateofbirth': SplitDateWidget(),
        }

        fields = ('first_name', 'last_name', 'sex', 'dateofbirth', 'email',
                  'phonenumber', 'street', 'postalcode', 'city', 'country', 'send_me_email',
                  'skype', 'msn', 'jabber')



    first_name = forms.CharField(max_length=50,
                                 widget=forms.TextInput(),
                                 label=_(u'First name'),
                                 required=True)

    last_name = forms.CharField(max_length=50,
                                widget=forms.TextInput(),
                                label=_(u'Last name'),
                                required=True)

    phonenumber = forms.RegexField(label=_(u'Phonenumber'),
                                   required=False,
                                   regex=r'(\+[0-9]{2}( )?)?([0-9]{8})')

    send_me_email = forms.BooleanField(widget=forms.CheckboxInput(),
                                       label=_(u'Inform me about events and other important changes.'),
                                       initial=True,
                                       required=False)

    def __init__(self, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)

        self.helper = S2FormHelper(horizontal=True)

        layout = S2Layout(
            S2Fieldset(_('Personal info'),
                       'first_name', 'last_name', 'sex', 'dateofbirth', collapse=False),
            S2Fieldset(_('Contact'),
                       'email', 'phonenumber', 'msn', 'skype', 'jabber', collapse=False),
            S2Fieldset(_('Address'),
                       'street', 'postalcode', 'city', 'country', collapse=False),
            S2Fieldset(None,
                       'send_me_email', collapse=False))

        self.helper.add_layout(layout)
        self.helper.form_tag = False


class UserWebsiteFormSet(BaseInlineFormSet):

    helper = S2FormHelper(horizontal=True)

    layout = S2Layout(
        S2Fieldset(None,
                   'name', 'url', 'DELETE', collapse=False))

    helper.add_layout(layout)
    helper.form_tag = False

UserWebsiteFormSet = inlineformset_factory(User, UserWebsite, formset=UserWebsiteFormSet, extra=2)


