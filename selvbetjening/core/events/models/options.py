# coding=UTF-8

from datetime import datetime

from django.utils.translation import ugettext as _
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.utils import timezone

from event import Event

from attendee import Attend, AttendState


class OptionGroup(models.Model):

    class Meta:
        ordering = ('order',)  # ordered by "order" ascending
        app_label = 'events'

    event = models.ForeignKey(Event)
    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True)

    minimum_selected = models.IntegerField(_('Minimum selected'), default=0)
    maximum_selected = models.IntegerField(_('Maximum selected'), default=0)

    maximum_attendees = models.IntegerField(_('Maximum attendees'), default=0)

    freeze_time = models.DateTimeField(_('Freeze time'), blank=True, null=True)
    order = models.IntegerField(_('Order'), default=0)

    # A package is a way to select all options in the group collectively, at an
    # alternative price. This is purely "virtual", e.g. we never record that a
    # member selected a package explicitly.
    # If a user selects a package, we select all options for the user and
    # interpret this as the user selecting the package. Thus, if the user selects
    # all options, we will automatically convert this into him selecting the package.
    package_solution = models.BooleanField(default=False)
    package_price = models.DecimalField(default=0, max_digits=6, decimal_places=2)

    public_statistic = models.BooleanField(default=False)
    lock_selections_on_acceptance = models.BooleanField(default=False)

    @property
    def attendees(self):
        return Attend.objects.filter(selection__option__group=self.pk).distinct()

    @property
    def accepted_attendees(self):
        return self.attendees.exclude(state=AttendState.waiting)

    @property
    def options(self):
        return self.option_set.select_related().order_by('order')

    def is_frozen(self):
        if self.freeze_time is None:
            return False
        else:
            return timezone.now() > self.freeze_time

    # business logic related to limitations

    def max_attendees_reached(self):
        return self.maximum_attendees > 0 and self.accepted_attendees.count() >= self.maximum_attendees

    def __unicode__(self):
        return u'%s' % self.name


class Option(models.Model):

    class Meta:
        ordering = ('order',)
        app_label = 'events'

    group = models.ForeignKey(OptionGroup)
    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True)

    freeze_time = models.DateTimeField(_('Freeze time'), blank=True, null=True)
    maximum_attendees = models.IntegerField(_('Maximum attendees'), blank=True, null=True)

    price = models.DecimalField(default=0, max_digits=6, decimal_places=2)

    order = models.IntegerField(_('Order'), default=0)

    @property
    def selections(self):
        return self.selection_set.all()

    @property
    def limited_selections(self):
        return self.selections.exclude(attendee__state=AttendState.waiting)

    @property
    def suboptions(self):
        return self.suboption_set.all()

    @property
    def paid_selections(self):
        paid_selections = []
        for selection in self.selections:
            if selection.attendee.invoice.is_paid():
                paid_selections.append(selection)

        return paid_selections

    def is_frozen(self):
        if self.group.is_frozen():
            return True

        if self.freeze_time is None:
            return False
        else:
            return datetime.now() > self.freeze_time

    def max_attendees_reached(self):
        if self.group.max_attendees_reached():
            return True

        if self.maximum_attendees is not None and \
                self.maximum_attendees > 0 and \
                self.limited_selections.count() >= self.maximum_attendees:

            return True
        else:
            return False

    def paid_selections_count(self):
        return len(self.paid_selections)

    def __unicode__(self):
        return u'%s: %s' % (self.group.event.title, self.name)


class SubOption(models.Model):

    class Meta:
        app_label = 'events'

    option = models.ForeignKey(Option)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2,
                                blank=True, null=True, default=None)

    @property
    def selections(self):
        return self.selection_set.all()

    def __unicode__(self):
        return u'%s' % self.name


class Selection(models.Model):

    class Meta:
        app_label = 'events'

    attendee = models.ForeignKey(Attend)
    option = models.ForeignKey(Option)
    suboption = models.ForeignKey(SubOption, blank=True, null=True)

    @property
    def price(self):
        if self.suboption is not None and \
           self.suboption.price is not None:
            return self.suboption.price
        else:
            return self.option.price

    class Meta:
        unique_together = (('attendee', 'option'))

    def __unicode__(self):
        if self.suboption:
            return u'%s (%s)' % (self.option, self.suboption)
        else:
            return u'%s' % self.option


def update_invoice_handler(sender, **kwargs):
    instance = kwargs['instance']

    try:
        instance.attendee.invoice.update()
    except Attend.DoesNotExist:
        pass

post_delete.connect(update_invoice_handler, sender=Selection)
post_save.connect(update_invoice_handler, sender=Selection)