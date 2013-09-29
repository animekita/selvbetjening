# coding=UTF-8

"""

    Options
    - A dynamic data model for events


    The options system is used to extend an event with a data model unique to that event.

    A user defined data model
    =========================

    An event is associated with one or more option groups, and each option group is associated with one or more options.

    An option is a single distinct input (of some type) for which a value can be provided for an attendee. E.g.
    you could add an option such as "Wants to help with the event" with a boolean type. Each attendee can then
    provide either a true or a false value for this option.

    We support the following types:
    - Boolean values (checkbox)
    - Text
    - Choices (selector)

    An option group is a logical cluster of options used for displaying options in logical groups and to apply
    scopes, and invariants collectively to a group of options.

    A special anonymous option group can be added (forced to be the first group in any ordering). This can be used
    for various unmarked options (placement is enforced for display purposes).

    This system is not 100% flexible, however it should be sufficient in most cases.

    All fields can be set to be "selected by default at registration".

    Scope (who can see and who can edit what)
    =========================================

    Not all data should be exposed everywhere, thus view and edit rights are given explicitly to different scopes.

    Scope checks is exposed directly on the options and option groups.

    View scopes:
    - Registration
    - Edit registration
    - User invoice
    - System invoice (invoice in sadmin)

    Edit scopes: (Edit automatically implies view rights)
    - Registration
    - Edit registration (while waiting)
    - Edit registration (while accepted)
    - Edit registration (while attended)

    Invariants on data
    ===================

    A number of invariants can be stated on option group and option level. These invariants are enforced for
    end-users (sadmin can bypass these).

    All option types has a notion of being selected. Booleans are selected when true, text inputs are selected
    if non-empty, and choices are selected when any value is selected.

    Option Group
    ------------

    - Option group gatekeeper (disables or enables an entire option group, if disabled it deletes all other selections)
    - Maximum selected
    - Minimum selected


    Effects
    =======

    It is possible to define prices associated with selection various items. The prices are added to the users
    invoice.

    Important: All options with a price must be visible on user invoices, otherwise the price will not be added
    to the invoice!

    - Each option has a price that is added if the option is selected.
    - Each option group has a package price (modifier) applied if all items in a package is selected.
    - Each suboption (choices) has a price (modifier) applied if chosen.

    Change management
    =================

    Changing the data model when in use is not without risk. Thus, strict rules are enforced in sadmin and direct
    changes to OptionGroup and Option should be avoided at all costs!

    In general, the rules are as follows:

    - Renaming titles and descriptions is allowed and will result in updates to existing invoices
    - Changing prices is allowed and will result in updates to existing invoices

    The following is allowed, hover it can possibly violate invariants (and those violations will not be acted upon)

    - Deleting options is allowed and will result in updates to existing invoices

    Tools are provided for mass changes to existing selections.



"""

from django.utils.translation import ugettext as _
from django.db import models

from event import Event

from attendee import Attend


class OptionGroup(models.Model):

    class Meta:
        ordering = ('order',)  # ordered by "order" ascending
        app_label = 'events'

    event = models.ForeignKey(Event)

    # Data model

    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True)

    order = models.IntegerField(_('Order'), default=0)

    # Invariants on data

    minimum_selected = models.IntegerField(_('Minimum selected'), default=0)
    maximum_selected = models.IntegerField(_('Maximum selected'), default=0)

    gatekeeper = models.ForeignKey('events.Option', blank=True, null=True)

    # Effects

    # A package price modifier - if all options in a group are selected then we will
    # apply this special package price modifier. We interpret this as disabled if set to 0.
    package_price = models.DecimalField(default=0, max_digits=6, decimal_places=2)

    # Special

    is_special = models.BooleanField(_('Special option group'), default=False)

    @property
    def options(self):
        return self.option_set.select_related().order_by('order')

    def save(self, *args, **kwargs):

        if self.is_special:
            self.name = ''
            self.description = ''
            self.order = -100  # a quick and dirty ordering hack, all other orders are >= 0

        super(OptionGroup, self).save(*args, **kwargs)


class Option(models.Model):

    class Meta:
        ordering = ('order',)
        app_label = 'events'

    TYPE_CHOICES = (
        ('boolean', _('Boolean')),
        ('choices', _('Choices')),
        ('text', _('Text'))
    )

    group = models.ForeignKey(OptionGroup)

    # Data model

    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True)

    order = models.IntegerField(_('Order'), default=0)

    type = models.CharField(_('Type'), max_length=32, choices=TYPE_CHOICES, default='boolean')

    # Scopes, default settings equals to the "disabled" preset

    in_scope_view_registration = models.BooleanField(default=False)
    in_scope_view_manage = models.BooleanField(default=False)
    in_scope_view_user_invoice = models.BooleanField(default=False)
    in_scope_view_system_invoice = models.BooleanField(default=True)

    in_scope_edit_registration = models.BooleanField(default=False)
    in_scope_edit_manage_waiting = models.BooleanField(default=False)
    in_scope_edit_manage_accepted = models.BooleanField(default=False)
    in_scope_edit_manage_attended = models.BooleanField(default=False)

    # Selected by default

    selected_by_default = models.BooleanField(default=False)

    # Effects

    price = models.DecimalField(default=0, max_digits=6, decimal_places=2)

    @property
    def selections(self):
        return self.selection_set.all()

    @property
    def suboptions(self):
        return self.suboption_set.all()

    def __unicode__(self):
        return u'%s: %s' % (self.group.event.title, self.name)


class SubOption(models.Model):

    class Meta:
        app_label = 'events'

    option = models.ForeignKey(Option)

    # Data model

    name = models.CharField(max_length=255)

    # Effect

    price = models.DecimalField(max_digits=6, decimal_places=2,
                                blank=True, null=True, default=None)

    def __unicode__(self):
        return u'%s' % self.name


class Selection(models.Model):

    class Meta:
        unique_together = (('attendee', 'option'))
        app_label = 'events'

    attendee = models.ForeignKey(Attend)
    option = models.ForeignKey(Option)

    text = models.CharField(max_length=255, blank=True)
    suboption = models.ForeignKey(SubOption, blank=True, null=True)

    @property
    def price(self):
        if self.suboption is not None and \
           self.suboption.price is not None:
            return self.option.price + self.suboption.price
        else:
            return self.option.price

    def __unicode__(self):
        if self.suboption:
            return u'%s (%s)' % (self.option, self.suboption)
        else:
            return u'%s' % self.option

