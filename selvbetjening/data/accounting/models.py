from datetime import datetime, timedelta

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

class MembershipState(object):
    INACTIVE = 'INACTIVE'
    PASSIVE = 'PASSIVE'
    CONDITIONAL_ACTIVE = 'CONDITIONAL_ACTIVE'
    ACTIVE = 'ACTIVE'

class PaymentManager(models.Manager):
    def get_membership_state(self, user):
        if not hasattr(user, 'payment_set'):
            return MembershipState.INACTIVE

        payments = user.payment_set.order_by('-timestamp')
        if len(payments) == 0:
            return MembershipState.INACTIVE

        if payments[0].type == 'SRATE':
            pay = payments[1]
        else:
            pay = payments[0]

        payment_quater = self.total_quaters(pay.timestamp)
        date_in_quaters = self.total_quaters(datetime.now())

        if payment_quater + 8 <= date_in_quaters:
            return MembershipState.INACTIVE
        elif payment_quater + 4 <= date_in_quaters:
            return MembershipState.PASSIVE
        else:
            if payments[0].type == 'FULL' or payments[0].type == 'SRATE':
                return MembershipState.ACTIVE
            else:
                return MembershipState.CONDITIONAL_ACTIVE

    def last_member_period(self, user):
        """ Returns the timestamp marking the beginning of the last user membership period """
        payments = user.payment_set.order_by('-timestamp')
        if len(payments) == 0:
            return None

        if payments[0].type == 'SRATE':
            return payments[1].timestamp
        else:
            return payments[0].timestamp

    def member_since(self, user):
        last_payment_timestamp = self.last_member_period(user)

        if last_payment_timestamp is None:
            return None

        payment_quater = self.total_quaters(last_payment_timestamp)

        if payment_quater + 4 <= self.total_quaters(datetime.now()):
            return None
        else:
            return last_payment_timestamp

    def member_to(self, user):
        timestamp = self.member_since(user)
        if timestamp is not None:
            year = timestamp.year + 1
            month = (self.to_quarter(timestamp) - 1) * 3 + 1
            return datetime(year, month, 1).date() - timedelta(days=1)
        else:
            return None

    def passive_to(self, user):
        last_payment_timestamp = self.last_member_period(user)
        if last_payment_timestamp is not None:
            year = last_payment_timestamp.year + 2
            month = (self.to_quarter(last_payment_timestamp) - 1) * 3 + 1
            return datetime(year, month, 1).date() - timedelta(days=1)
        else:
            return None

    def to_quarter(self, date):
        return ((date.month-1) / 3) + 1

    def total_quaters(self, timestamp):
        return timestamp.year * 4 + self.to_quarter(timestamp)

class Payment(models.Model):
    """
    Two types of payments can be used, full (one time) payment or rate
    (divided into two rates) payment.

    The first rate of the rate payment method is paied at a specific event,
    and the second payment must be paied at the second event. The timestamp
    is used to determine which event the payment is associated to.
    """

    TYPE_CHOICES = (
        ('FULL', 'Full'),
        ('FRATE', 'First rate'),
        ('SRATE', 'Second rate'),
    )

    user = models.ForeignKey(User, verbose_name=_(u'user'))
    timestamp = models.DateTimeField()
    type = 	models.CharField(max_length=5, choices=TYPE_CHOICES)

    objects = PaymentManager()

    def get_ammount(self):
        yearlyRate = YearlyRate.objects.filter(year=self.timestamp.year)[0]
        if self.type == 'FULL':
            return yearlyRate.rate
        else:
            return yearlyRate.rate / 2

class YearlyRate(models.Model):
    year = models.IntegerField(max_length=4)
    rate = models.IntegerField()

    def __unicode__(self):
        return _(u"Yearly rate for %s") % self.year