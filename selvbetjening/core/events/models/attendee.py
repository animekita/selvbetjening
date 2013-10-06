# coding=UTF-8

from datetime import datetime

from django.contrib.auth.models import User
from django.db.models.aggregates import Sum
from django.utils.translation import ugettext as _
from django.db import models

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

    def recalculate_aggregations_price(self, attendees):

        attendees = attendees.annotate(price_actual=Sum('selection__option__price'))

        for attendee in attendees:
            attendee.price = attendee.price_actual if attendee.price_actual is not None else 0
            attendee.save()

    def recalculate_aggregations_paid(self, attendees):

        attendees = attendees.annotate(paid_actual=Sum('payment__amount'))

        for attendee in attendees:
            attendee.paid = attendee.paid_actual if attendee.paid_actual is not None else 0
            attendee.save()


class Attend(models.Model):

    class Meta:
        unique_together = ('event', 'user')
        app_label = 'events'

    event = models.ForeignKey(Event)
    user = models.ForeignKey(User)

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

    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    paid = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    # Payment inspections

    @property
    def unpaid(self):
        return self.price - self.paid

    @property
    def overpaid(self):
        return self.paid - self.price

    # TODO should we reduce the set of inspections a bit?
    def is_paid(self):
        return self.paid >= self.price

    def in_balance(self):
        return self.paid == self.price

    def is_overpaid(self):
        return self.paid > self.price

    def is_partial(self):
        return self.paid > 0 and not self.is_paid()

    def is_unpaid(self):
        return self.paid == 0 and not self.price == 0

    def recalculate_price(self):
        result = self.selections.aggregate(price=Sum('option__price'))

        self.price = result['price']
        self.save()

    objects = AttendManager()

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
