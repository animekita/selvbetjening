# coding=UTF-8

import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save

from countries.models import Country
from sorl.thumbnail.fields import ThumbnailField

import signals

def to_age(dateofbirth, reference_date=None):
    if reference_date is None:
        reference_date = datetime.date.today()

    if dateofbirth is None:
        return None

    bday = dateofbirth
    d = reference_date
    return (d.year - bday.year) - int((d.month, d.day) < (bday.month, bday.day))

class UserWebsite(models.Model):
    user = models.ForeignKey(User, verbose_name=_(u'user'), db_column='user_id')

    name = models.CharField(max_length=32)
    url = models.URLField()

class UserCommunication(models.Model):
    METHOD_CHOICES = (('skype', 'skype'),
                      ('msn', 'MSN'),
                      ('jabber', 'Jabber'),)

    user = models.ForeignKey(User, verbose_name=_(u'user'), db_column='user_id')

    method = models.CharField(max_length=12, choices=METHOD_CHOICES)
    identification = models.CharField(max_length=255)

    class Meta:
        unique_together = ('method', 'user')

class UserProfile(models.Model):
    SEX = (('', ''), ('male', _('male')), ('female', _('female')))

    user = models.ForeignKey(User, unique=True, verbose_name=_(u'user'), db_column='user_id', primary_key=True)

    dateofbirth = models.DateField(_(u'date of birth'), blank=True, null=True)

    sex = models.CharField(_(u'sex'), blank=True, max_length=6, choices=SEX, default='')

    street = models.CharField(_(u'street'), max_length=255, blank=True)
    postalcode = models.PositiveIntegerField(_(u'postal code'), blank=True, null=True)
    city = models.CharField(_(u'city'), max_length=255, blank=True)
    country = models.ForeignKey(Country, default='DK', blank=True, null=True)

    phonenumber = models.CharField(_(u'phonenumber'), max_length=32, blank=True, null=True)

    send_me_email = models.BooleanField(_(u'Send me emails'))

    picture = ThumbnailField(upload_to='pictures/', blank=True, size=(260,260), quality=100)

    class Meta:
        verbose_name = _(u'user profile')
        verbose_name_plural = _(u'user profiles')

    def get_age(self, at_date=None):
        return to_age(self.dateofbirth, at_date)
    get_age.admin_order_field = 'dateofbirth'

    def __unicode__(self):
        return _(u'Registration profile for %s') % self.user

    def save(self, *args, **kwargs):
        picture = None

        try:
            old = UserProfile.objects.get(pk=self.pk)
            if old.picture != self.picture:
                old.picture.delete()
        except:
            pass

        super(UserProfile, self).save(*args, **kwargs)

class UserLocation(models.Model):
    user = models.OneToOneField(User, related_name='location')
    lat = models.FloatField(blank=True, null=True, default=None)
    lng = models.FloatField(blank=True, null=True, default=None)
    expired = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now=True)

def profile_saved(sender, **kwargs):
    profile = kwargs['instance']

    try:
        location = UserLocation.objects.get(user=profile.user)
        location.expired = True
        location.save()

    except UserLocation.DoesNotExist:
        UserLocation.objects.create(user=profile.user, expired=True)

post_save.connect(profile_saved, sender=UserProfile)