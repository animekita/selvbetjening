# coding=UTF-8

from django.dispatch import receiver
from django.db.models.signals import Signal

from attendee import Attend

request_attendee_pks_signal = Signal(providing_args=['attendee'])
find_attendee_signal = Signal(providing_args=['pk'])

@receiver(request_attendee_pks_signal)
def basic_pks_handler(sender, **kwargs):
    attendee = kwargs['attendee']
    return 'Attendee ID', str(attendee.pk)

@receiver(find_attendee_signal)
def basic_find_attendee_handler(sender, **kwargs):
    try:
        pk = int(kwargs['pk'])
        return 'Attendee ID', Attend.objects.get(pk=pk)

    except:
        return None
