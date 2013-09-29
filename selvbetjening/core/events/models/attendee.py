# coding=UTF-8

from datetime import datetime

from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.db import models

from selvbetjening.core.invoice.models import Invoice

from event import Event, AttendeeAcceptPolicy


class AttendState(object):
    waiting = 'waiting'
    accepted = 'accepted'
    attended = 'attended'

    accepted_states = (accepted, attended)

    @staticmethod
    def get_choices():
        return (
            (AttendState.waiting, _(u'Waiting')),
            (AttendState.accepted, _(u'Accepted')),
            (AttendState.attended, _(u'Attended'))
        )


class AttendManager(models.Manager):

    def all_related(self):
        return self.all().select_related().\
            prefetch_related('invoice__payment_set').\
            prefetch_related('invoice__line_set')

    def can_register_to_event(self, event):

        max_attendees_reached = event.maximum_attendees != 0 and \
            event.maximum_attendees <= event.attendees.exclude(state=AttendState.waiting).count()

        return event.is_registration_open() and not max_attendees_reached


class Attend(models.Model):

    class Meta:
        unique_together = ('event', 'user')
        app_label = 'events'

    event = models.ForeignKey(Event)
    user = models.ForeignKey(User)

    # TODO add a new state such that deleted attendences still exist (such that we can pay people back)
    # TODO remove invoices
    invoice = models.ForeignKey(Invoice, blank=True)

    state = models.CharField(max_length=32,
                             choices=AttendState.get_choices(),
                             default=AttendState.waiting)

    # TODO fix this property, the logic related to it is flawed!
    is_new = models.BooleanField(default=None, blank=True)  # the correct value is set by save()

    # Updates when state changes to and from "waiting".
    # This is used when ordering the accepted and waiting attendee
    # lists. The django API can't query the attend_history
    # effectively so this is used as an alternative.
    # TODO Please find a fix to this mess!
    change_timestamp = models.DateTimeField(null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True, null=True)

    changed = models.DateTimeField(null=True, blank=True)

    objects = AttendManager()

    @property
    def price(self):
        return self.invoice.total_price

    @property
    def paid(self):
        return self.invoice.paid

    @property
    def selections(self):
        return self.selection_set.all()

    @property
    def comments(self):
        return self.comment_set.all()

    # option management

    def select_option(self, option, suboption=None):
        selection, created = self.selection_set.get_or_create(option=option,
                                                              defaults={'suboption': suboption})

        if not created and selection.suboption != suboption:
            selection.suboption = suboption
            selection.save()

        return selection

    def deselect_option(self, option):
        self.selection_set.filter(option=option).delete()

    def save(self, *args, **kwargs):

        try:
            invoice_set = self.invoice is not None
        except Invoice.DoesNotExist:
            invoice_set = False

        if not invoice_set:
            self.invoice = Invoice.objects.create(name=unicode(self.event), user=self.user)

        # TODO this mechanism does not seem to robust, do we ever update existing entries to have a correct value?
        if self.is_new is None:
            self.is_new = self.user.attend_set.all().count() == 0

        if self.event.move_to_accepted_policy == AttendeeAcceptPolicy.always and\
                self.state not in AttendState.accepted_states:

            self.state = AttendState.accepted

        try:
            latest = self.state_history.latest('timestamp')

            if (latest.state == AttendState.waiting and (self.state == AttendState.accepted or self.state == AttendState.attended)) or \
               ((latest.state == AttendState.accepted or latest.state == AttendState.attended) and self.state == AttendState.waiting):
                self.change_timestamp = datetime.now()

            super(Attend, self).save(*args, **kwargs)

            if not latest.state == self.state:
                AttendStateChange.objects.create(state=self.state,
                                                 attendee=self)

        except AttendStateChange.DoesNotExist:
            self.change_timestamp = datetime.now()
            super(Attend, self).save(*args, **kwargs)

            AttendStateChange.objects.create(state=self.state,
                                             attendee=self)

    def __unicode__(self):
        return u'%s' % self.user


class AttendStateChange(models.Model):

    class Meta:
        app_label = 'events'

    timestamp = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=32,
                             choices=AttendState.get_choices())
    attendee = models.ForeignKey(Attend, related_name='state_history')


class AttendeeComment(models.Model):

    class Meta:
        app_label = 'events'

    attendee = models.ForeignKey(Attend, related_name='comment_set')

    author = models.CharField(max_length=256)
    comment = models.TextField()

    timestamp = models.DateTimeField(auto_now_add=True)
