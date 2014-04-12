import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from selvbetjening.core.events.models import Attend

logger = logging.getLogger('selvbetjening.events')


class Payment(models.Model):

    class Meta:
        app_label = 'events'

    user = models.ForeignKey(get_user_model())
    attendee = models.ForeignKey(Attend, null=True, on_delete=models.SET_NULL)  # store abandoned payments

    amount = models.DecimalField(max_digits=6, decimal_places=2)

    signee = models.ForeignKey(get_user_model(), null=True, blank=True, related_name='signee_payment_set')
    note = models.CharField(max_length=256, blank=True)

    created_date = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=Payment)
def payment_save_handler(sender, **kwargs):
    instance = kwargs.get('instance')
    created = kwargs.get('created')

    try:
        if created:
            logger.info('Payment registered (%s,-) -- %s', instance.amount, instance.note,
                extra={
                    'related_user': instance.user,
                    'related_attendee': instance.attendee
                })

    except ObjectDoesNotExist:
        pass