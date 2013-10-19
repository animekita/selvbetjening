
try:
    import thread
except ImportError:
    import dummy_thread as thread

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from event import Event, Group
from attendee import Attend, AttendState, AttendeeComment, AttendStateChange, AttendeeAcceptPolicy
from options import OptionGroup, Option, SubOption, Selection
from payment import Payment
from payment_keys import request_attendee_pks_signal, find_attendee_signal

__ALL__ = ['Group', 'Event', 'Attend', 'OptionGroup', 'Option', 'SubOption', 'Selection', 'AttendComment',
           'AttendState', 'AttendStateChange', 'request_attendee_pks_signal', 'find_attendee_signal',
           'suspend_price_updates', 'resume_price_updates']

# Global update modes
# This is used to disable automatic updates of attendee prices
# through selection and deselection of options.
# Only use these through the disable/enable provided in decorators.

_disable_automatic_price_updates = {}


def is_price_updates_suspended():
    return _disable_automatic_price_updates.get(thread.get_ident(), False)


def suspend_price_updates():
    _disable_automatic_price_updates[thread.get_ident()] = True


def resume_price_updates():
    _disable_automatic_price_updates.pop(thread.get_ident(), None)


# signal handlers


@receiver(post_save, sender=Selection, dispatch_uid='increase_price_on_selection')
def increase_price_on_selection(sender, **kwargs):
    selection = kwargs['instance']

    if is_price_updates_suspended():
        return

    if selection.price != 0:
        selection.attendee.price += selection.price
        selection.attendee.save()


@receiver(post_delete, sender=Selection, dispatch_uid='decrease_price_on_deselect')
def decrease_price_on_deselect(sender, **kwargs):
    selection = kwargs['instance']

    if is_price_updates_suspended():
        return

    if selection.price != 0:
        selection.attendee.price -= selection.price
        selection.attendee.save()


@receiver(post_save, sender=Payment, dispatch_uid='update_paid_and_update_state_on_payment')
def update_paid_and_update_state_on_payment(sender, **kwargs):
    payment = kwargs['instance']
    created = kwargs['created']

    if payment.attendee is None:
        return

    if created:
        attendee = payment.attendee

        attendee.paid += payment.amount
        attendee.save()

        if attendee.event.move_to_accepted_policy == AttendeeAcceptPolicy.on_payment and \
            attendee.state == AttendState.waiting:

            attendee.state = AttendState.accepted
            attendee.save()


@receiver(post_save, sender=Option, dispatch_uid='update_prices_on_price_change')
def update_prices_on_price_change(sender, **kwargs):
    option = kwargs['instance']
    created = kwargs['created']

    if created:
        return

    # TODO enable this somewhere, we can't do this on every option save - that would crash the manage options page

    ##Attend.objects.recalculate_aggregations_price(
    ##    Attend.objects.filter(selection__option=option)
    ##)
