# coding=UTF-8

from django.dispatch import receiver
from django.db.models.signals import Signal

request_attendee_pks_signal = Signal(providing_args=['attendee'])
find_attendee_signal = Signal(providing_args=['pk'])


@receiver(request_attendee_pks_signal)
def basic_pks_handler(sender, **kwargs):
    attendee = kwargs['attendee']
    return 'Attendee ID', str(attendee.pk)


@receiver(find_attendee_signal)
def basic_find_attendee_handler(sender, **kwargs):
    from selvbetjening.core.events.models.attendee import Attend

    try:
        pk = int(kwargs['pk'])
        return 'Attendee ID', Attend.objects.get(pk=pk)

    except:
        return None


def eua_pks_handler(sender, **kwargs):
    attendee = kwargs['attendee']
    key = 'EUA.%s.%s.%s' % (attendee.event.pk,
                            attendee.user.pk,
                            attendee.pk)

    return 'EUA ID', key

request_attendee_pks_signal.connect(eua_pks_handler)


def eua_find_attendee_handler(sender, **kwargs):
    from selvbetjening.core.events.models.attendee import Attend
    
    pk = kwargs['pk']

    try:
        label, event_pk, user_pk, attendee_pk = pk.split('.')

        if label != 'EUA':
            return None

        attendee = Attend.objects.get(
            pk=attendee_pk,
            user__pk=user_pk,
            event__pk=event_pk)

        return 'EUA', attendee

    except:
        return None

find_attendee_signal.connect(eua_find_attendee_handler)