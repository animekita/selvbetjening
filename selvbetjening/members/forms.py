# coding=UTF-8

from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.forms import PasswordChangeForm as AuthPasswordChangeForm

from models import UserProfile, EmailChangeRequest
import signals

class ProfileForm(forms.Form):
    """
    Form for editing the user profile information
    """
    first_name = forms.CharField(max_length=50,
                          widget=forms.TextInput(),
                          label=_(u'first name'),
                          required=True)
    last_name = forms.CharField(max_length=50,
                          widget=forms.TextInput(),
                          label=_(u'last name'),
                          required=True)
    dateofbirth = forms.DateField(widget=forms.TextInput(),
                                  label=_(u'date of birth'),
                                  input_formats=('%d/%m/%Y', '%d/%m/%y', '%d.%m.%Y', '%d.%m.%y', '%d-%m-%Y', '%d-%m-%y'),
                                  help_text=_(u'State your date of birth using the format %(format)s.') % {'format' : 'dd-mm-yyyy'})

    street = forms.CharField(max_length=50,
                             widget=forms.TextInput(),
                             label=_(u'street'),
                             required=False)
    postalcode = forms.IntegerField(label=_(u'postal code'), required=False)

    city = forms.CharField(max_length=255,
                           widget=forms.TextInput(),
                           label=_(u'city'),
                           required=False)
    phonenumber = forms.IntegerField(label=_(u'phonenumber'), required=False)

    send_me_email = forms.BooleanField(widget=forms.CheckboxInput(),
                             label=_(u'Inform me about events and other important changes in Anime Kita.'),
                             initial=True, required=False)

    class Meta:
        layout = ((_(u'personal information'), ('first_name', 'last_name', 'dateofbirth', 'phonenumber')),
                  (_(u'address'), ('street', 'postalcode', 'city')),
                  (_(u'other'), ('send_me_email', ))
                       )

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

        profile = user.get_profile()
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

class EmailChangeForm(forms.Form):
    """
    Change email form
    """
    new_email = forms.EmailField(max_length=75,
                                widget=forms.TextInput(),
                                label=_(u'new email'))
    password = forms.CharField(max_length=255,
                               widget=forms.PasswordInput(),
                               label=_(u'password'))

    def __init__(self, data=None, auto_id='id_%s', prefix=None, initial=None, user=None):
        super(EmailChangeForm, self).__init__(data=data, auto_id=auto_id, prefix=prefix, initial=initial)

        self.userModel = user

    def clean_password(self):
        if self.userModel.check_password(self.cleaned_data['password']):
            return self.cleaned_data['password']
        else:
            raise forms.ValidationError(_(u'Wrong password'))

    def save(self):
        """
        Save and return the newly generated key
        """
        return EmailChangeRequest.objects.create_request(self.userModel, self.cleaned_data['new_email'])

class PasswordChangeForm(AuthPasswordChangeForm):

    def save(self, commit=True):
        super(PasswordChangeForm, self).save(commit)
        signals.user_changed_password.send(self, user=self.user, password=self.cleaned_data['new_password1'])
