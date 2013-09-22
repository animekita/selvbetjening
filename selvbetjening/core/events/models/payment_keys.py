# coding=UTF-8

from django.db.models.signals import Signal

from attendee import Attend

request_attendee_pks_signal = Signal(providing_args=['attendee'])


def basic_pks_handler(sender, **kwargs):
    attendee = kwargs['attendee']

    return 'Invoice ID', str(attendee.invoice.pk)

request_attendee_pks_signal.connect(basic_pks_handler)


def legacy_attendee_pks_handler(sender, **kwargs):
    attendee = kwargs['attendee']
    key = '%s.%s.%s' % (attendee.invoice.latest_revision.pk,
                        attendee.invoice.pk,
                        attendee.user.pk)

    return 'Legacy ID', key

request_attendee_pks_signal.connect(legacy_attendee_pks_handler)

find_attendee_signal = Signal(providing_args=['pk'])


def basic_find_attendee_handler(sender, **kwargs):
    try:
        pk = int(kwargs['pk'])
        return 'Invoice ID', Attend.objects.get(pk=pk)

    except:
        return None

find_attendee_signal.connect(basic_find_attendee_handler)


def legacy_find_attendee_handler(sender, **kwargs):
    pk=kwargs['pk']

    try:
        revision_pk, invoice_pk, user_pk = pk.split('.')

        attendee = Attend.objects.get(user__pk=user_pk,
                                      invoice__pk=invoice_pk,
                                      invoice__revision_set__pk=revision_pk)

        return 'Legacy', attendee

    except:
        return None

find_attendee_signal.connect(legacy_find_attendee_handler)

