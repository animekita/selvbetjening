# coding=UTF-8

"""
Forms and validation code for user registration.

"""
from django import forms
from django.core.validators import alnum_re
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from members.forms import ProfileForm
from members.models import UserProfile, EmailChangeRequest
from registration.models import RegistrationProfile
from core import models as coremodel
from events.forms import SignupForm

class RegistrationForm(ProfileForm):
    """ Form for registering a new user account. """

    username = forms.CharField(max_length=30,
                               widget=forms.TextInput(),
                               label=_(u"username"),
                               help_text=_(u"Your username can only contain the characters a-z, underscore and numbers."))
    password1 = forms.CharField(widget=forms.PasswordInput(),
                                label=_(u"password"))
    password2 = forms.CharField(widget=forms.PasswordInput(),
                                label=_(u"verify password"))
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(maxlength=75)),
                             label=_(u"email"))

    tos = forms.BooleanField(widget=forms.CheckboxInput(),
                             label=_(u"I allow Anime Kita to store my personal information."))

    class Meta:
        layout = ((_(u"personal information"), ('first_name', 'last_name', 'dateofbirth', 'phonenumber', 'email', 'send_me_email')),
                  (_(u"address"), ('street', 'postalcode', 'city')),
                  (_(u"user"), ('username', 'password1', 'password2')),
               (_(u"data management terms"), ('tos', ))
                       )

    def clean_tos(self):
        if self.cleaned_data.get('tos', False):
            return self.cleaned_data['tos']
        raise forms.ValidationError(_(u"You must allow us to store your information to create an account."))
    def clean_username(self):
        """
        Validates that the username is alphanumeric and is not already
        in use.

        """
        if not alnum_re.search(self.cleaned_data['username']):
            raise forms.ValidationError(_(u'Usernames can only contain letters, numbers and underscores'))

        # Check the vanilla forum for existing users
        if not self.hook_valid_forum_username(self.cleaned_data["username"]):
            raise forms.ValidationError(_(u'This username is already taken. Please choose another.'))

        # Check the "selvbetjening" database for existing users
        try:
            user = User.objects.get(username__exact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_(u'This username is already taken. Please choose another.'))

    def hook_valid_forum_username(self, checkUsername):
        vf = coremodel.VanillaForum()
        return not vf.userExists(checkUsername)

    def clean_password2(self):
        """
        Validates that the two password inputs match.

        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] == self.cleaned_data['password2']:
                return self.cleaned_data['password2']
            raise forms.ValidationError(_(u"You must type the same password each time"))

    def save(self):
        """
        Creates the new ``User`` and ``RegistrationProfile``, and
        returns the ``User``.

        """
        return RegistrationProfile.objects.create_inactive_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            email=self.cleaned_data['email'],
            dateofbirth=self.cleaned_data['dateofbirth'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            street=self.cleaned_data['street'],
            postalcode=self.cleaned_data['postalcode'],
            city=self.cleaned_data['city'],
            phonenumber=self.cleaned_data['phonenumber'],
            send_me_email=self.cleaned_data['send_me_email'])

class CreateForm(RegistrationForm):
    """ Create user, skipping email validation. """

    def save(self):
        user = RegistrationProfile.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            email=self.cleaned_data['email'],
            dateofbirth=self.cleaned_data['dateofbirth'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            street=self.cleaned_data['street'],
            postalcode=self.cleaned_data['postalcode'],
            city=self.cleaned_data['city'],
            phonenumber=self.cleaned_data['phonenumber'],
            send_me_email=self.cleaned_data['send_me_email'])
        
        RegistrationProfile.objects.create_forum_user(user, RegistrationProfile.objects.prepare_password_for_forum(self.cleaned_data['password1']))
        
        return user

