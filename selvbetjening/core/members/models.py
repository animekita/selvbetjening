# coding=UTF-8

import datetime
from django.contrib.auth import get_user_model

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save

from countries.models import Country

from selvbetjening.core.user.models import SUser

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
    user = models.ForeignKey(get_user_model(), verbose_name=_(u'user'), db_column='user_id')

    name = models.CharField(max_length=32, blank=True)
    url = models.URLField(blank=True)


class UserLocation(models.Model):
    user = models.OneToOneField(get_user_model(), related_name='location')
    lat = models.FloatField(blank=True, null=True, default=None)
    lng = models.FloatField(blank=True, null=True, default=None)
    expired = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now=True)


def user_saved(sender, **kwargs):
    user = kwargs['instance']

    try:
        location = UserLocation.objects.get(user=user)
        location.expired = True
        location.save()

    except UserLocation.DoesNotExist:
        UserLocation.objects.create(user=user, expired=True)

post_save.connect(user_saved, sender=SUser)