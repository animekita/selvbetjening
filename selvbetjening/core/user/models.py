import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext as _

from sorl.thumbnail.fields import ThumbnailField

from countries.models import Country


def to_age(dateofbirth, reference_date=None):
    if reference_date is None:
        reference_date = datetime.date.today()

    if dateofbirth is None:
        return None

    bday = dateofbirth
    d = reference_date
    return (d.year - bday.year) - int((d.month, d.day) < (bday.month, bday.day))


class SUser(AbstractUser):

    SEX = (('male', _('male')), ('female', _('female')))

    dateofbirth = models.DateField(_(u'date of birth'), blank=True, null=True)

    sex = models.CharField(_(u'sex'), blank=True, max_length=6, choices=SEX, default='')

    street = models.CharField(_(u'street'), max_length=255, blank=True)
    postalcode = models.PositiveIntegerField(_(u'postal code'), blank=True, null=True)
    city = models.CharField(_(u'city'), max_length=255, blank=True)
    country = models.ForeignKey(Country, default='DK', blank=True, null=True)

    phonenumber = models.CharField(_(u'phonenumber'), max_length=32, blank=True, null=True)

    skype = models.CharField(max_length=255, blank=True)
    jabber = models.CharField(max_length=255, blank=True)
    msn = models.CharField(max_length=255, blank=True)

    send_me_email = models.BooleanField(_(u'Send me emails'))

    picture = ThumbnailField(_(u'Picture'),
                             upload_to='pictures/',
                             blank=True, size=(260,260), quality=100)

    def get_age(self, at_date=None):
        return to_age(self.dateofbirth, at_date)
    get_age.admin_order_field = 'dateofbirth'

    def __unicode__(self):
        return self.username

# TODO picture deletion logic?