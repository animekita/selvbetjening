# coding=UTF-8

import datetime, sha

from django.db import models
from django.db.models import permalink

from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User                                     # for the  userprofile's foreignkey field
from django.template.loader import render_to_string

from core import models as coremodels
from accounting.models import Payment

class UserProfile(models.Model):
    """
    Model containing user data

    """
    user = models.ForeignKey(User, unique=True, verbose_name=_(u'user'))
    dateofbirth = models.DateField(_(u'date of birth'))
    street = models.CharField(_(u'street'), max_length=255, blank=True)
    postalcode = models.PositiveIntegerField(_(u'postal code'), blank=True, null=True)
    city = models.CharField(_(u'city'), max_length=255, blank=True)
    phonenumber = models.PositiveIntegerField(_(u'phonenumber'), blank=True, null=True)
    send_me_email = models.BooleanField(_(u'Send me emails'))

    class Meta:
        verbose_name = _(u'user profile')
        verbose_name_plural = _(u'user profiles')

    def __unicode__(self):
        return _(u"Registration profile for %s") % self.user

    def age (self, d=datetime.date.today()):
        bday = self.dateofbirth
        return (d.year - bday.year) - int((d.month, d.day) < (bday.month, bday.day))

    def isUnderaged(self, date = datetime.date.today()):
        return (self.age(date) < 15)

    def get_membership_state(self):
        return Payment.objects.get_membership_state(self.user)

    def member_since(self):
        return Payment.objects.member_since(self.user)

class EmailChangeRequestManager(models.Manager):

    def create_request(self, user, new_email):
        """
        Creates a new email change request, and returns the key
        """
        timestamp = datetime.datetime.now()
        key = sha.new(timestamp.__str__() + new_email).hexdigest()
        ecr = EmailChangeRequest.objects.create(user=user, new_email=new_email, key=key, timestamp=timestamp)

        from django.core.mail import EmailMultiAlternatives, SMTPConnection
        current_site = Site.objects.get_current()

        subject = render_to_string('members/change_email_subject.txt',
                                   { 'site': current_site })
        subject = ''.join(subject.splitlines()) # remove newlines from subject

        message = render_to_string('members/change_email.txt',
                                   { 'key': key,
                                     'user':user,
                                     'ecr':ecr,
                                     'new_email':new_email,
                                     'site': current_site,
                                 "site_url":settings.SITE_URL})
        message_html = render_to_string('members/change_email.html.txt',
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
    user = models.ForeignKey(User, verbose_name=_(u'user'))
    new_email= models.CharField(_(u'email'), max_length=75)
    key = models.CharField(_(u'key'), max_length=40)
    timestamp = models.DateTimeField(_(u'timestamp'))

    objects = EmailChangeRequestManager()

    def get_absolute_url(self):
        return ("members_change_email_confirm", (), { "key" : self.key })
    get_absolute_url = permalink(get_absolute_url)

    class Meta:
        verbose_name = _(u'email change request')
        verbose_name_plural = _(u'email change requests')

    class Admin:
        pass

    def __unicode__(self):
        return _(u"Email change request or %s") % self.user