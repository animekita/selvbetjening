# coding=UTF-8

import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

import signals

def get_age (self, at_date=None):
    if at_date is None:
        at_date = datetime.date.today()

    bday = self.dateofbirth
    d = at_date
    return (d.year - bday.year) - int((d.month, d.day) < (bday.month, bday.day))

class UserProfileManager(models.Manager):
    def create(self, **kwargs):
        user = kwargs['user']
        try:
            return user.get_profile()
        except ObjectDoesNotExist:
            return super(UserProfileManager, self).create(**kwargs)

class UserProfile(models.Model):
    """ DEPRECATED! Use extended user! """

    user = models.ForeignKey(User, unique=True, verbose_name=_(u'user'), db_column='user_ptr_id', primary_key=True)

    dateofbirth = models.DateField(_(u'date of birth'), blank=True, null=True)
    street = models.CharField(_(u'street'), max_length=255, blank=True)
    postalcode = models.PositiveIntegerField(_(u'postal code'), blank=True, null=True)
    city = models.CharField(_(u'city'), max_length=255, blank=True)
    phonenumber = models.PositiveIntegerField(_(u'phonenumber'), blank=True, null=True)
    send_me_email = models.BooleanField(_(u'Send me emails'))

    objects = UserProfileManager()

    class Meta:
        verbose_name = _(u'user profile')
        verbose_name_plural = _(u'user profiles')

    get_age = get_age
    get_age.admin_order_field = 'dateofbirth'

    def __unicode__(self):
        return _(u'Registration profile for %s') % self.user

class ExtendedUser(User):
    dateofbirth = models.DateField(_(u'date of birth'), blank=True, null=True)
    street = models.CharField(_(u'street'), max_length=255, blank=True)
    postalcode = models.PositiveIntegerField(_(u'postal code'), blank=True, null=True)
    city = models.CharField(_(u'city'), max_length=255, blank=True)
    phonenumber = models.PositiveIntegerField(_(u'phonenumber'), blank=True, null=True)
    send_me_email = models.BooleanField(_(u'Send me emails'))

    class Meta:
        verbose_name = _(u'Extended user')
        verbose_name_plural = _(u'Extended users')
        managed = False
        db_table = 'members_userprofile'

    get_age = get_age

def create_profile(sender, **kwargs):
    if kwargs.get('created', False):
        user = kwargs['instance']
        UserProfile.objects.create(user=user,)

post_save.connect(create_profile, sender=User)