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
        payments = user.payment_set.order_by('-timestamp')
        if len(payments) == 0:
            return MembershipState.INACTIVE
        
        if payments[0].type == 'SRATE':
            pay = payments[1]
        else:
            pay = payments[0]   
    
        if self.total_quaters(pay.timestamp) + 8 <= self.total_quaters(datetime.now()):
            return MembershipState.INACTIVE
        elif self.total_quaters(pay.timestamp) + 4 <= self.total_quaters(datetime.now()):
            return MembershipState.PASSIVE
        else:
            if payments[0].type == 'FULL' or payments[0].type == 'SRATE':
                return MembershipState.ACTIVE
            else:
                return MembershipState.CONDITIONAL_ACTIVE
    
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
    type = models.CharField(max_length=5)
    
    objects = PaymentManager()
    
    class Admin:
        pass

class YearlyRate(models.Model):
    year = models.IntegerField(max_length=4)
    rate = models.IntegerField()
    
    def __unicode__(self):
        return _(u"Yearly rate for %s") % self.year
    
    class Admin:
        list_display = ('__str__', 'year', 'rate')
    