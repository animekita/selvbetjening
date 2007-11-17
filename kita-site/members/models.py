# coding=UTF-8

import datetime, random, re, sha, md5

from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.db.models import permalink
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from core import models as coremodels

SHA1_RE = re.compile('^[a-f0-9]{40}$')

""" 
The registrationManager and Profile are based on code from http://django-registration.googlecode.com.
"""

class RegistrationManager(models.Manager):
    """
    Custom manager for the ``RegistrationProfile`` model.
    """
    
    def activate_user(self, activation_key):
        """
        Validates an activation key and activates the corresponding
        ``User`` if valid.
        
        If the key is valid and has not expired, returns the ``User``
        after activating the user, creating a forum account and 
        deleting the key.
        
        If the key is not valid or has expired, returns ``False``
        """
        
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        # @remark Should we do this here? or in the view using the model... <sema>
        if SHA1_RE.search(activation_key):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            
            if not profile.activation_key_expired():
                # activate user
                user = profile.user
                user.is_active = True
                user.save()
                
                # create forum user
                vf = coremodels.VanillaForum()
                vf.createUser(Name = user.username, Password=profile.forumPass, Email=user.email, FirstName=user.first_name, LastName=user.last_name)
                
                profile.delete()
                return user
            
            return False
    
    def create_inactive_user(self, username, password, email, dateofbirth, last_name, first_name, city, street, postalcode, phonenumber):
        """
        Creates a new, inactive ``User``, generates a
        ``RegistrationProfile`` and emails its activation key to the
        ``User``. Returns the new ``User``.
        
        """
        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.save()
        
        registration_profile = self.create_profile(new_user, password)
        
        UserProfile.objects.create(user=new_user, dateofbirth=dateofbirth, city=city, street=street, postalcode=postalcode, phonenumber=phonenumber)
        
        # send email
        from django.core.mail import EmailMultiAlternatives, SMTPConnection
        current_site = Site.objects.get_current()
        
        subject = render_to_string('registration/activation_email_subject.txt',
                                   { 'site': current_site })
        
        subject = ''.join(subject.splitlines()) # remove newlines from subject
        
        message = render_to_string('registration/activation_email.txt',
                                   { 'activation_key': registration_profile.activation_key,
                                     'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                                     'first_name': first_name,
                                     'username': username,
                                     'site': current_site,
                                     'site_url':settings.SITE_URL})
        
        message_html = render_to_string('registration/activation_email.html.txt',
                                   { 'activation_key': registration_profile.activation_key,
                                     'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                                     'first_name': first_name,
                                     'username': username,
                                     'site': current_site,
                                     'site_url':settings.SITE_URL}) 
            
        msg = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [new_user.email])
        msg.attach_alternative(message_html, "text/html")
        
        connection = SMTPConnection()
        connection.send_messages([msg])        
        
        return new_user
    
    def create_profile(self, user, forumPassword):
        """
        Creates a ``RegistrationProfile`` for a given
        ``User``. Returns the ``RegistrationProfile``.
        
        The activation key for the ``RegistrationProfile`` will be a
        SHA1 hash, generated from a combination of the ``User``'s
        username and a random salt.
        
        """
        salt = sha.new(str(random.random())).hexdigest()[:5]
        activation_key = sha.new(salt+user.username).hexdigest()
        passwd = md5.new(forumPassword)
        return self.create(user=user,
                           activation_key=activation_key,
                           forumPass=passwd.hexdigest())
        
    def delete_expired_users(self):
        """
        Removes expired instances of ``RegistrationProfile`` and their
        associated ``User``s.
        
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
    activation_key = models.CharField(_('activation key'), maxlength=40)
    forumPass = models.CharField(_('vanilla forum password'), maxlength=40)
    
    objects = RegistrationManager()
    
    class Meta:
        verbose_name = _('registration profile')
        verbose_name_plural = _('registration profiles')
    
    class Admin:
        list_display = ('__str__', 'activation_key_expired')
        search_fields = ('user__username', 'user__first_name')
        
    def __unicode__(self):
        return u"Registration information for %s" % self.user
    
    def activation_key_expired(self):
        """
        Determines whether this ``RegistrationProfile``'s activation
        key has expired.
        
        Returns ``True`` if the key has expired, ``False`` otherwise.
        
        Key expiration is determined by the setting
        ``ACCOUNT_ACTIVATION_DAYS``, which should be the number of
        days a key should remain valid after an account is registered.
        
        """
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.user.date_joined + expiration_date <= datetime.datetime.now()
    activation_key_expired.boolean = True

class UserProfile(models.Model):
    """
    Model containing user data
    
    """
    user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
    dateofbirth = models.DateField(_('date of birth'))
    street = models.CharField(_('street'), max_length=255, blank=True)
    postalcode = models.PositiveIntegerField(_('postal code'), blank=True, null=True)
    city = models.CharField(_('city'), max_length=255, blank=True)
    phonenumber = models.PositiveIntegerField(_('phonenumber'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
    
    class Admin:
        fields = (
            (None, {'fields' : ('user', 'dateofbirth', 'phonenumber')}),
            ('Address', {'classes' : 'collapse', 
                         'fields' : ('street', 'postalcode', 'city')}
            ),
        )

    def __unicode__(self):
        return u"Registration profile for %s" % self.user
    
    def age (self, d=datetime.date.today()):
        bday = self.dateofbirth
        return (d.year - bday.year) - int((d.month, d.day) < (bday.month, bday.day))

class EmailChangeRequestManager(models.Manager):
    
    def create_request(self, user, new_email):
        """
        Creates a new email change request, and returns the key
        """
        timestamp = datetime.datetime.now()
        key = sha.new(timestamp.__str__() + new_email + "very secret text 123").hexdigest()
        ecr = EmailChangeRequest.objects.create(user=user, new_email=new_email, key=key, timestamp=timestamp)
        
        from django.core.mail import EmailMultiAlternatives, SMTPConnection
        current_site = Site.objects.get_current()
        
        subject = render_to_string('registration/change_email_subject.txt',
                                   { 'site': current_site })
        subject = ''.join(subject.splitlines()) # remove newlines from subject
        
        message = render_to_string('registration/change_email.txt',
                                   { 'key': key,
                                     'user':user,
                                     'ecr':ecr,
                                     'new_email':new_email,
                                     'site': current_site,
                                 "site_url":settings.SITE_URL})
        message_html = render_to_string('registration/change_email.html.txt',
                                   { 'key': key,
                                     'user':user,
                                     'ecr':ecr,
                                     'new_email':new_email,
                                     'site': current_site,
                                     "site_url":settings.SITE_URL,
                                 })
        
        msg = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        msg.attach_alternative(message_html, "text/html")
        
        connection = SMTPConnection()
        connection.send_messages([msg])
        return key
    
    def confirm(self, key):
        """
        Confirms if the key is in the database. If it is found the user email will be updated and the key removed. Returns true on success and false on failure.
        """
        try:
            ecr = EmailChangeRequest.objects.select_related().get(key=key)
        except models.ObjectDoesNotExist:
            return False
        except AssertionError:
            return False
        
        # set the new user email and save the user object
        ecr.user.email = ecr.new_email
        ecr.user.save()
        
        # set the new email for the forum system
        vf = coremodels.VanillaForum()
        vf.changeUserEmail(ecr.user.username, ecr.new_email)
        
        # delete the ecr request
        ecr.delete()
        
        return True

class EmailChangeRequest(models.Model):
    user = models.ForeignKey(User, verbose_name=_('user'))
    new_email= models.CharField(_('email'), max_length=75)
    key = models.CharField(_('key'), max_length=40)
    timestamp = models.DateTimeField(_('timestamp'))

    objects = EmailChangeRequestManager()

    def get_absolute_url(self):
        return ("members_change_email_confirm", (), { "key" : self.key })
    get_absolute_url = permalink(get_absolute_url)

    class Meta:
        verbose_name = _('email change request')
        verbose_name_plural = _('email change requests')
        
    class Admin:
        pass
    
    def __unicode__(self):
        return u'Email change request or %s' % self.user
    
    