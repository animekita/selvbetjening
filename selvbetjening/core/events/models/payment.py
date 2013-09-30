
from django.db import models
from django.contrib.auth.models import User

from selvbetjening.core.events.models import Attend


class Payment(models.Model):

    class Meta:
        app_label = 'events'

    user = models.ForeignKey(User)
    attendee = models.ForeignKey(Attend, null=True, on_delete=models.SET_NULL)  # store abandoned payments

    amount = models.DecimalField(max_digits=6, decimal_places=2)

    signee = models.ForeignKey(User, null=True, blank=True, related_name='signee_payment_set')
    note = models.CharField(max_length=256, blank=True)

    created_date = models.DateTimeField(auto_now_add=True)