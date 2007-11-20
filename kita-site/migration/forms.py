from django import newforms as forms
from django.core.validators import alnum_re
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from members import forms as memberforms
from members.models import RegistrationProfile

from core import models as coremodels

class VanillaForumForm(forms.Form):
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
        if hasattr(self.cleaned_data, "username") and hasattr(self.cleaned_data, "password") and not vf.authenticateUser(self.cleaned_data["username"], self.cleaned_data["password"]):
            raise forms.ValidationError(_(u"Please enter a correct username and password."))
        
        return self.cleaned_data

class MigrationForm(memberforms.RegistrationForm):

    username = forms.CharField(max_length=30,
                               widget=forms.TextInput(attrs={"disabled":"true"}),
                               label=_(u"username"))

    def __init__(self, *args, **kwargs): 
        self.currentUsername = kwargs["user"]
        del kwargs["user"]
        
        super(memberforms.RegistrationForm, self).__init__(*args, **kwargs)

    def clean_username(self):
  
        return self.cleaned_data["username"]
        
    
    def save(self):
        # update the forum profile
        vf = coremodels.VanillaForum()
        vf.updateUser(self.currentUsername, 
                      self.cleaned_data["password1"], 
                      self.cleaned_data["email"],
                      self.cleaned_data["first_name"], 
                      self.cleaned_data["last_name"])
        
        # save the normal user profile, and let him verify his email before being able to use the main account...
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
    
