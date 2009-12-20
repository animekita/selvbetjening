# coding=UTF-8

import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from countries.models import Country

import signals

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, verbose_name=_(u'user'), db_column='user_id', primary_key=True)

    dateofbirth = models.DateField(_(u'date of birth'), blank=True, null=True)
    street = models.CharField(_(u'street'), max_length=255, blank=True)
    postalcode = models.PositiveIntegerField(_(u'postal code'), blank=True, null=True)
    city = models.CharField(_(u'city'), max_length=255, blank=True)
    country = models.ForeignKey(Country, default='DK', blank=True, null=True)
    phonenumber = models.PositiveIntegerField(_(u'phonenumber'), blank=True, null=True)
    send_me_email = models.BooleanField(_(u'Send me emails'))

    class Meta:
        verbose_name = _(u'user profile')
        verbose_name_plural = _(u'user profiles')

    def get_age (self, at_date=None):
        if at_date is None:
            at_date = datetime.date.today()

        bday = self.dateofbirth
        d = at_date
        return (d.year - bday.year) - int((d.month, d.day) < (bday.month, bday.day))
    get_age.admin_order_field = 'dateofbirth'

    def __unicode__(self):
        return _(u'Registration profile for %s') % self.user
