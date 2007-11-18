# coding=UTF-8

"""
Forms and validation code for user registration.

"""


from django import newforms as forms
from django.core.validators import alnum_re
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from members.models import RegistrationProfile, UserProfile, EmailChangeRequest

from core import models as coremodel

attrs_dict = { 'class': 'required' }

class ProfileChangeEmailForm(forms.Form):
    """
    Change email form
    """
    new_email = forms.EmailField(max_length=75,
                                widget=forms.TextInput(),
                                label=_(u'email'))
    password = forms.CharField(max_length=255,
                               widget=forms.PasswordInput(),
                               label=_(u'password'))
    
    def __init__(self, data=None, auto_id='id_%s', prefix=None, initial=None, user=None):
        super(ProfileChangeEmailForm, self).__init__(data=data, auto_id=auto_id, prefix=prefix, initial=initial)
        
        self.userModel = user
    
    def clean_password(self):
        if self.userModel.check_password(self.cleaned_data['password']):
            return self.cleaned_data['password']
        else:
            raise forms.ValidationError(_(u'Wrong password'))
    
    class Admin:
        pass
    
    
    def save(self):
        """
        Save and return the newly generated key
        """
        return EmailChangeRequest.objects.create_request(self.userModel, self.cleaned_data['new_email'])

class ProfileForm(forms.Form):
    """
    Form for editing the user profile information
    """
    first_name = forms.CharField(max_length=50,
                          widget=forms.TextInput(attrs=attrs_dict),
                          label=_(u'first name'),
                          required=True)
    last_name = forms.CharField(max_length=50,
                          widget=forms.TextInput(attrs=attrs_dict),
                          label=_(u'last name'), 
                          required=True)    
    dateofbirth = forms.DateField(widget=forms.TextInput(attrs=attrs_dict),
                                  label=_(u'date of birth'), 
                                  input_formats=('%d/%m/%Y', '%d/%m/%y', '%d.%m.%Y', '%d.%m.%y', '%d-%m-%Y', '%d-%m-%y'),
                                  help_text=_(u"State your date of birth using the format %(format)s.") % {"format" : "dd-mm-yyyy"})

    street = forms.CharField(max_length=50,
                             widget=forms.TextInput(),
                             label=_(u"street"),
                             required=False)
    postalcode = forms.IntegerField(label=_(u"postal code"), required=False)
    
    city = forms.CharField(max_length=255,
                           widget=forms.TextInput(),
                           label=_(u"city"),
                           required=False)
    phonenumber = forms.IntegerField(label=_(u"phonenumber"), required=False)
    
    class Meta:
        layout = ((_(u"Personal information"), ('first_name', 'last_name', 'dateofbirth', 'phonenumber')),
                  (_(u"Address"), ('street', 'city',  'postalcode')),
                       )
    
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
            profile.save()
        else:
            UserProfile.objects.create(user=user, 
                                       dateofbirth=dateofbirth, 
                                       city=city, street=street, 
                                       postalcode=postalcode, 
                                       phonenumber=phonenumber)
    
class RegistrationForm(ProfileForm):
    """
    Form for registering a new user account.
    
    """

    username = forms.CharField(max_length=30,
                               widget=forms.TextInput(attrs=attrs_dict),
                               label=_(u"username"),
                               help_text=_(u"Your username can only contain the characters a-z, underscore and numbers."))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict),
                                label=_(u"password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict),
                                label=_(u"verify password"))
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=75)),
                             label=_(u"email"))
    
    class Meta:
        layout = ((_(u"personal information"), ('first_name', 'last_name', 'dateofbirth', 'phonenumber', 'email')),
                  (_(u"address"), ('street', 'city',  'postalcode')),
                  (_(u"user"), ('username', 'password1', 'password2'))
                       )
        
    def clean_username(self):
        """
        Validates that the username is alphanumeric and is not already
        in use.
        
        """
        if not alnum_re.search(self.cleaned_data['username']):
            raise forms.ValidationError(_(u'Usernames can only contain letters, numbers and underscores'))
        
        # Check the vanilla forum for existing users
        vf = coremodel.VanillaForum()
        if vf.userExists(self.cleaned_data["username"]):
            raise forms.ValidationError(_(u'This username is already taken. Please choose another.'))
        
        # Check the "selvbetjening" database for existing users
        # All users should have a forum and selvbetjening account, so this step is redundant. 
        # But just in case, check both databases.
        try:
            user = User.objects.get(username__exact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_(u'This username is already taken. Please choose another.'))
    
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
        return RegistrationProfile.objects.create_inactive_user(username=self.cleaned_data['username'],
                                                                    password=self.cleaned_data['password1'],
                                                                    email=self.cleaned_data['email'],
                                                                    dateofbirth=self.cleaned_data['dateofbirth'],
                                                                    first_name=self.cleaned_data['first_name'],
                                                                    last_name=self.cleaned_data['last_name'],
                                                                    street=self.cleaned_data['street'],
                                                                    postalcode=self.cleaned_data['postalcode'],
                                                                    city=self.cleaned_data['city'],
                                                                    phonenumber=self.cleaned_data['phonenumber'],
                                                                )
    
class PasswordChangeForm(forms.Form):
    """
    A form that lets a user change his password.
    Stolen from the django.contrib.auth package and rewritten to use newforms.
    """

    old_password = forms.CharField(max_length=30, widget=forms.PasswordInput(), label=_(u"password"))
    new_password1 = forms.CharField(max_length=30, widget=forms.PasswordInput(), label=_(u"new password"))
    new_password2 = forms.CharField(max_length=30, widget=forms.PasswordInput(), label=_(u"verify password"))
    
    def __init__(self, *args, **kwargs): 
        self.user= kwargs["user"]
        del kwargs["user"]
        
        super(forms.Form, self).__init__(*args, **kwargs)

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        if not self.user.check_password(self.cleaned_data["old_password"]):
            raise forms.ValidationError(_("Your old password was entered incorrectly. Please enter it again."))
    
    def clean(self):
        """
        Validates that new_password1 and new_password2 are identical.
        """
        if "new_password1" in self.cleaned_data and  "new_password2" in self.cleaned_data:
            if self.cleaned_data["new_password1"] != self.cleaned_data["new_password2"]:
                raise forms.ValidationError(_(u"You must type the same password each time"))
    
        return self.cleaned_data

    def save(self):
        """
        Saves the new password.
        """
        self.user.set_password(self.cleaned_data["new_password1"])
        self.user.save()
        
        # set the new password for the forum
        vf = coremodel.VanillaForum()
        vf.changeUserPassword(self.user.username, self.cleaned_data["new_password1"])