# coding=UTF-8
import re

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.db.models import OneToOneRel

from countries.models import Country
from uni_form.helpers import FormHelper, Submit, Fieldset, Layout, Row

from selvbetjening.viewhelpers.forms import widgets

from models import UserProfile
from shortcuts import get_or_create_profile
import signals

class ProfileForm(forms.Form):
    COUNTRY_CHOICES = [(country.pk, str(country)) for country in Country.objects.only('printable_name')]

    first_name = forms.CharField(max_length=50,
                          widget=forms.TextInput(),
                          label=_(u'first name'),
                          required=True)
    last_name = forms.CharField(max_length=50,
                          widget=forms.TextInput(),
                          label=_(u'last name'),
                          required=True)

    email = forms.EmailField(max_length=75, label=_(u'email'))

    dateofbirth = forms.DateField(widget=widgets.UniformSelectDateWidget(years=range(1910, 2010)),
                                  label=_(u'date of birth'))

    street = forms.CharField(max_length=50,
                             widget=forms.TextInput(),
                             label=_(u'street'),
                             required=False)
    postalcode = forms.IntegerField(label=_(u'postal code'), required=False)

    city = forms.CharField(max_length=255,
                           widget=forms.TextInput(),
                           label=_(u'city'),
                           required=False)

    country = forms.ChoiceField(label=_(u'country'),
                                choices=COUNTRY_CHOICES,
                                required=False, initial='DK',)

    phonenumber = forms.IntegerField(label=_(u'phonenumber'), required=False)

    send_me_email = forms.BooleanField(widget=forms.CheckboxInput(),
                             label=_(u'Inform me about events and other important changes.'),
                             initial=True, required=False)

    layout = Layout(Fieldset(_(u'Personal Information'),
                             'first_name', 'last_name', 'dateofbirth', 'phonenumber'),
                    Fieldset(_(u'Address'),
                             'street', 'postalcode', 'city', 'country'),
                    Fieldset(_(u'Other'),
                             'email', 'send_me_email'))

    submit = Submit(_('Change personal information'), _('Change personal information'))

    helper = FormHelper()
    helper.use_csrf_protection = True
    helper.add_input(submit)
    helper.add_layout(layout)

    def clean_dateofbirth(self):
        # The birth year must be above 1900 to be compatible with strftime
        if self.cleaned_data['dateofbirth'].year < 1900:
            raise forms.ValidationError(_(u'Your birthday is not allowed to be dated before 1900'))

        return self.cleaned_data['dateofbirth']

    def save(self, user):
        """
        Update user profile and user records
        """
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        profile = get_or_create_profile(user)
        if profile is not None:
            profile.dateofbirth = self.cleaned_data['dateofbirth']
            profile.street = self.cleaned_data['street']
            profile.postalcode = self.cleaned_data['postalcode']
            profile.city = self.cleaned_data['city']
            profile.phonenumber = self.cleaned_data['phonenumber']
            profile.send_me_email = self.cleaned_data['send_me_email']
            profile.save()
        else:
            UserProfile.objects.create(user=user,
                                       dateofbirth=self.cleaned_data['dateofbirth'],
                                       city=self.cleaned_data['city'],
                                       street=self.cleaned_data['street'],
                                       postalcode=self.cleaned_data['postalcode'],
                                       phonenumber=self.cleaned_data['phonenumber'],
                                       send_me_email=self.cleaned_data['send_me_email'])

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

    layout = Layout(Fieldset(_(u"personal information"),
                             'first_name', 'last_name', 'dateofbirth', 'phonenumber', 'email', 'send_me_email'),
                    Fieldset(_(u"address"),
                             'street', 'postalcode', 'city', 'country'),
                    Fieldset(_(u"user"),
                             'username', 'password1', 'password2'),
                    Fieldset(_(u"data management terms"),
                             'tos'))

    helper = FormHelper()

    submit = Submit(_('Create user'), _('Create user'))
    helper.add_input(submit)
    helper.use_csrf_protection = True
    helper.add_layout(layout)

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

        signals.user_created.send(sender=self,
                                  instance=user,
                                  clear_text_password=self.cleaned_data["password1"])

        return user

class AdminSelectMigrationUsers(forms.Form):
    old_user = forms.IntegerField(label=_('Old user account'), widget=ForeignKeyRawIdWidget(OneToOneRel(User, 'id')))
    new_user = forms.IntegerField(label=_('New user account'), widget=ForeignKeyRawIdWidget(OneToOneRel(User, 'id')))

    def clean(self):
        try:
            if self.cleaned_data['old_user'] == self.cleaned_data['new_user']:
                raise forms.ValidationError(_('Old user account and new user account must be different'))

        except KeyError:
            pass # if old_user or new_user is not set, then another error should have shown itself

        return self.cleaned_data

