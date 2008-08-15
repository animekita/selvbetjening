from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from registration.forms import RegistrationForm
from registration.models import RegistrationProfile

from core import models as coremodels

class VanillaForumForm(forms.Form):
    """
    Login form for the migrations script

    Is valid if the given credentials matches an existing forum user,
    a selvbetjening user with the same username does not exist.

    """
    username = forms.CharField(max_length=30,
                               widget=forms.TextInput(),
                               label=_(u"username"))

    password = forms.CharField(widget=forms.PasswordInput(),
                               label=_(u"password"))

    def clean_username(self):
        # We cant migrate forum users which already have an account in the selvbetjening system.
        try:
            user = User.objects.get(username__exact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username'];

        raise forms.ValidationError(_(u"This user has already migrated."))

    def clean(self):
        vf = coremodels.VanillaForum()
        if not vf.authenticateUser(self.cleaned_data.get('username', ''), self.cleaned_data.get('password', '')):
            raise forms.ValidationError(_(u"Please enter a correct username and password."))

        return self.cleaned_data

class MigrationForm(RegistrationForm):

    def __init__(self, *args, **kwargs):
        self.currentUsername = kwargs["user"]
        del kwargs["user"]

        RegistrationForm.__init__(self, *args, **kwargs)

    def hook_valid_forum_username(self, checkUsername):
        if checkUsername == self.currentUsername:
            return True

        return RegistrationForm.hook_valid_forum_username(self, checkUsername)

    def save(self):
        # update the forum profile
        vf = coremodels.VanillaForum()
        vf.updateUser(self.currentUsername,
                      self.cleaned_data["username"],
                      self.cleaned_data["password1"],
                      self.cleaned_data["email"],
                      self.cleaned_data["first_name"],
                      self.cleaned_data["last_name"])

        # save the normal user profile, and let him verify his email before being able to use the main account...
        return RegistrationForm.save(self)

