from django.db.models.signals import post_save, post_delete
from django.utils.translation import ugettext as _

from selvbetjening.core.invoice.signals import populate_invoice
from selvbetjening.core.invoice.models import Payment
from selvbetjening.core.mailcenter.sources import Source

from event import Event, Group
from attendee import Attend, AttendState, AttendeeComment, AttendStateChange, AttendeeAcceptPolicy
from options import OptionGroup, Option, SubOption, Selection
from payment_keys import request_attendee_pks_signal, find_attendee_signal

__ALL__ = ['Group', 'Event', 'Attend', 'OptionGroup', 'Option', 'SubOption', 'Selection', 'AttendComment',
           'AttendState', 'AttendStateChange', 'request_attendee_pks_signal', 'find_attendee_signal']


# email sources

attendes_event_source = Source('attends_event_signal',
                               _(u'User registers for event'),
                               [Attend])

payment_registered_source = Source('payment_registered',
                                   _(u'Payment registered'),
                                   [Attend, Payment])


# signal handlers


def update_invoice_handler(sender, **kwargs):
    instance = kwargs['instance']

    try:
        instance.attendee.invoice.update()
    except Attend.DoesNotExist:
        pass

post_delete.connect(update_invoice_handler, sender=Selection)
post_save.connect(update_invoice_handler, sender=Selection)


def update_invoice_with_attend_handler(sender, **kwargs):
    invoice = kwargs['invoice']

    for attendee in Attend.objects.filter(invoice=invoice):

        selections = attendee.selections.order_by('option__group__order',
                                                  'option__order',
                                                  'option__pk')

        selected_groups = set()
        selected_options = set()

        for selection in selections:
            if selection.option.group.package_solution:
                selected_groups.add(selection.option.group)
                selected_options.add(selection.option.pk)

        unselected_options = Option.objects.filter(group__in=selected_groups).\
                                            exclude(pk__in=selected_options)

        for option in unselected_options:
            try:
                selected_groups.remove(option.group)
            except KeyError:
                pass

        last_group = None

        for selection in selections:

            if last_group is not None and \
                    last_group != selection.option.group and \
                    last_group.package_solution and \
                    last_group in selected_groups:

                invoice.add_line(description=unicode(_(u'Package Discount')),
                                 group_name=unicode(last_group.name),
                                 price=last_group.package_price,
                                 managed=True)

            invoice.add_line(description=unicode(selection.option.name),
                             group_name=unicode(selection.option.group.name),
                             price=selection.price,
                             managed=True)

            last_group = selection.option.group

populate_invoice.connect(update_invoice_with_attend_handler)


def update_state_on_payment(sender, **kwargs):
    payment = kwargs['instance']
    created = kwargs['created']

    if created:
        attends = Attend.objects.filter(invoice=payment.invoice)
        attends = attends.filter(event__move_to_accepted_policy=AttendeeAcceptPolicy.on_payment)
        attends = attends.filter(state=AttendState.waiting)

        for attend in attends:
            attend.state = AttendState.accepted
            attend.save()

post_save.connect(update_state_on_payment, sender=Payment)

