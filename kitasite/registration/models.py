# coding=UTF-8

""" 
The registrationManager and Profile are heavily
modified versions of the registration code
from http://django-registration.googlecode.com.

"""

import datetime, random, re, sha, md5

from django.conf import settings
from django.db import models
from django.core.mail import EmailMultiAlternatives, SMTPConnection
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from members.models import UserProfile

from core import models as coremodels

class RegistrationManager(models.Manager):
    
    def activate_user(self, activation_key):
        """
        Validates an activation key and activates the corresponding
        ``User`` if valid.
        
        On successful activation, return the ``User`` object,
        creating a forum account and delete the key.
        
        On failure None is returned.
        
        """
        
        try:
            profile = self.get(activation_key=activation_key)
        except self.model.DoesNotExist:
            return None
        
        if not profile.activation_key_expired():
            user = profile.user
            user.is_active = True
            user.save()
            
            # Check if the forum-user already exists. (user migration)
            vf = coremodels.VanillaForum()
            if not vf.userExists(user.username):
                vf.createUser(Name = user.username, 
                              Password=profile.forumPass, 
                              Email=user.email, 
                              FirstName=user.first_name, 
                              LastName=user.last_name)
            
            profile.delete()
            return user
            
        return False  

    def create_user(self, username, password, email, dateofbirth, 
                    last_name, first_name, city, street, postalcode, 
                    phonenumber, send_me_email, is_active=True):
        
        user = User.objects.create_user(username, email, password)
        user.is_active = is_active
        user.first_name = first_name
        user.last_name = last_name
        user.save()
    
        UserProfile.objects.create(user=user, dateofbirth=dateofbirth, 
                                   city=city, street=street, postalcode=postalcode, 
                                   phonenumber=phonenumber, send_me_email=send_me_email)
        
        return user    
    
    def create_inactive_user(self, username, password, email, dateofbirth, 
                             last_name, first_name, city, street, postalcode, 
                             phonenumber, send_me_email):
        """
        Creates a new, inactive ``User``, generates a
        ``RegistrationProfile`` and emails its activation key to the
        ``User``. Returns the new ``User``.
        
        """
        
        user = self.create_user(username, password, email, dateofbirth, 
                                    last_name, first_name, city, street, postalcode, 
                                    phonenumber, send_me_email, is_active=False)
        
        registration_profile = self.create_registration_profile(user, password)
        
        self.send_activation_email(user, registration_profile)
        
        return user
        
    def send_activation_email(self, user, registration_profile):
        
        subject = render_to_string('registration/activation_email_subject.txt', { })
        subject = ''.join(subject.splitlines()) # remove newlines from subject
        
        message_data = { 'activation_key': registration_profile.activation_key,
                                     'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                                     'first_name': user.first_name,
                                     'last_name': user.last_name,
                                     'username': user.username,
                                     'site_url':settings.SITE_URL}
        
        message = render_to_string('registration/activation_email.txt', message_data)
        message_html = render_to_string('registration/activation_email.html.txt', message_data) 
            
        msg = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        msg.attach_alternative(message_html, "text/html")
        
        connection = SMTPConnection()
        connection.send_messages([msg])
    
    def create_registration_profile(self, user, forumPassword):
        """
        Returns the ``RegistrationProfile``.
        
        """
        salt = sha.new(str(random.random())).hexdigest()[:5]
        return self.create(user=user,
                           activation_key = sha.new(salt+user.username).hexdigest(),
                           forumPass = md5.new(forumPassword.encode('utf-8')).hexdigest())
        
    def delete_expired_users(self):
        """
        Accounts to be deleted are identified by searching for
        instances of ``RegistrationProfile`` with expired activation
        keys, and then checking to see if their associated ``User``
        instances have the field ``is_active`` set to ``False``; any
        ``User`` who is both inactive and has an expired activation
        key will be deleted.
        
        """
        for profile in self.all():
            if profile.activation_key_expired():
                user = profile.user
                if not user.is_active:
                    user.delete()


class RegistrationProfile(models.Model):
    """
    A simple profile which stores an activation key for use during
    user account registration.
    
    A md5 encrypted password is also stored, this is used for the
    Vanilla forum user profile.
    
    """
    user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
    activation_key = models.CharField(_('activation key'), max_length=40)
    forumPass = models.CharField(_('vanilla forum password'), max_length=40)
    
    objects = RegistrationManager()
    
    class Meta:
        verbose_name = _('registration profile')
        verbose_name_plural = _('registration profiles')
    
    class Admin:
        list_display = ('__str__', 'activation_key_expired')
        search_fields = ('user__username', 'user__first_name')
        
    def __unicode__(self):
        return _(u"Registration information for %s") % self.user
    
    def activation_key_expired(self):
        """
        Key expiration is determined by the setting
        ``ACCOUNT_ACTIVATION_DAYS``, which should be the number of
        days a key should remain valid after an account is registered.
        
        """
        
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.user.date_joined + expiration_date <= datetime.datetime.now()
    
    activation_key_expired.boolean = True
    