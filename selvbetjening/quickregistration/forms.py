# coding=UTF-8

"""
Forms and validation code for user registration.

"""
import re

from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from selvbetjening.members.forms import ProfileForm
from selvbetjening.members.models import UserProfile

import signals

username_re = re.compile("^[a-zA-Z0-9_]+$")

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

    tos = forms.BooleanField(widget=forms.CheckboxInput(),
                             label=_(u"I allow the storage of my personal information on this site."))

    class Meta:
        layout = ((_(u"personal information"), ('first_name', 'last_name',
                                                'dateofbirth', 'phonenumber',
                                                'email', 'send_me_email')),
                  (_(u"address"), ('street', 'postalcode', 'city')),
                  (_(u"user"), ('username', 'password1', 'password2')),
               (_(u"data management terms"), ('tos', ))
                       )

    def clean_tos(self):
        if not self.cleaned_data.get('tos', False):
            raise forms.ValidationError(_(u"You must allow us to store your information to create an account."))

        return self.cleaned_data['tos']

    def clean_username(self):
        """ Validates that the username is alphanumeric and is not in use. """

        if not username_re.match(self.cleaned_data['username']):
            raise forms.ValidationError(_(u'Usernames can only contain letters, numbers and underscores'))

        try:
            User.objects.get(username__exact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']

        raise forms.ValidationError(_(u'This username is already taken. Please choose another.'))

    def clean_password2(self):
        """ Validates that the two password inputs match. """

        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_(u"You must type the same password each time"))

            return self.cleaned_data['password2']

        return ''

    def save(self):
        user = User.objects.create_user(self.cleaned_data['username'],
                                        self.cleaned_data['email'],
                                        self.cleaned_data['password1'])

        user.is_active = True
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        UserProfile.objects.create(user=user,
                                   dateofbirth=self.cleaned_data['dateofbirth'],
                                   city=self.cleaned_data['city'],
                                   street=self.cleaned_data['street'],
                                   postalcode=self.cleaned_data['postalcode'],
                                   phonenumber=self.cleaned_data['phonenumber'],
                                   send_me_email=self.cleaned_data['send_me_email'])

        signals.user_created.send(self, user=user, password=self.cleaned_data["password1"])

        return user
