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

    The type of the input changes its behaviour in different contests. These behavioural changes are decided by
    a Type Manager, for which there is exactly one Type Manager associated with each type.

    An option group is a logical cluster of options used for displaying options in logical groups and to apply
    scopes, and invariants collectively to a group of options.

    A special anonymous option group can be added (forced to be the first group in any ordering). This can be used
    for various unmarked options (placement is enforced for display purposes).

    This system is not 100% flexible, however it should be sufficient in most cases.

    All option types has a notion of being selected. Booleans are selected when true, text inputs are selected
    if non-empty, and choices are selected when any value is selected.

    Scope (who can see and who can edit what)
    =========================================

    Not all data should be exposed everywhere, thus view and edit rights are given explicitly to different scopes.

    Scope checks is exposed directly on the options and option groups.

    View scopes:
    - Registration
    - Edit registration
    - User invoice
    - System invoice (invoice in sadmin)
    - Public statistics (show aggregated values for accepted attendees publicly)

    Edit scopes: (Edit automatically implies view rights)
    - Registration
    - Edit registration (while waiting)
    - Edit registration (while accepted)
    - Edit registration (while attended)

    Invariants on data
    ===================

    A number of invariants can be stated on option group and option level. These invariants are enforced for
    the users only (read, sadmin bypasses these).

    Option Group
    ------------

    - Option group gatekeeper (disables or enables an entire option group, if disabled it deletes all other selections)
    - Maximum selected
    - Minimum selected


    Effects (price)
    ===============

    An option can have a price. If the option is selected then that price will be added as a cost to the user's invoice.
    Suboptions also have prices that can modify the base price of the option.

    Important: All options with a price must be visible on user invoices, otherwise the price will not be added
    to the invoice!

    Change management
    =================

    Changing the data model when in use is not without risk. Thus, strict rules are enforced in sadmin and direct
    changes to OptionGroup and Option should be avoided at all costs!

    In general, the rules are as follows:

    - Renaming titles and descriptions is allowed and will result in updates to existing invoices
    - Changing prices is allowed and will result in updates to existing invoices

    One particular challenging problem is price calculation, since the total price for an attendee is cached
    in the database. This cached value is updated in three different ways:

    1. By a global recalculation of all attendee prices
    2. By a local recalculation of a single attendee (if the attendee changes her selections)
    3. By a global recalculation of attendee prices for a single option (if the price of an option is changed)


    TypeManagers
    ============

    A type manager encodes a set of rules for a type, mostly related to the display and interaction with a type.

    In general, all types are represented with the same set of basic building blocks
    - option with a price,
    - suboptions with individual prices
    - visibilty rules
    - a bit of text associated with each selection

    The type manager is allowed to decide the following:

    - Edit interface with the user and sadmin (widget)
      - And saving values into the backing store from said widget


"""
from django.db.models import F

from django.utils.translation import ugettext as _
from django.db import models

from event import Event

from attendee import Attend


class OptionGroup(models.Model):

    class Meta:
        ordering = ('-is_special', 'order',)  # ordered by "order" ascending (and always place specials first)
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
        ('text', _('Text')),
        ('autoselect', _('Auto Select')),
        ('autoselectchoice', _('Auto Select Choice'))
    )

    group = models.ForeignKey(OptionGroup)

    # Data model

    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True)

    order = models.IntegerField(_('Order'), default=0)

    type = models.CharField(_('Type'), max_length=32, choices=TYPE_CHOICES, default='boolean')

    # Scopes, default settings equals to the "disabled" preset

    in_scope_view_public = models.BooleanField(default=False)

    in_scope_view_registration = models.BooleanField(default=False)
    in_scope_view_manage = models.BooleanField(default=False)
    in_scope_view_user_invoice = models.BooleanField(default=False)
    in_scope_view_system_invoice = models.BooleanField(default=True)

    in_scope_edit_registration = models.BooleanField(default=False)
    in_scope_edit_manage_waiting = models.BooleanField(default=False)
    in_scope_edit_manage_accepted = models.BooleanField(default=False)
    in_scope_edit_manage_attended = models.BooleanField(default=False)

    # Effects

    price = models.DecimalField(default=0, max_digits=6, decimal_places=2,
                                help_text=_('This option will automatically be visible in user invoices and at check-in if a non-zero price is set.<br/><strong>Updating the price will affect existing attendees, and you are strongly encuraged to inform all attendees of such a change by e-mail.</strong>'))

    @property
    def selections(self):
        return self.selection_set.all()

    @property
    def suboptions(self):
        return self.suboption_set.all()

    def save(self, *args, **kwargs):

        # Invariants - enforce a number of invariants, silently
        # Yes that is bad, however some parts of the user interface is easier if this is silent

        # Edit permission expects view permission
        if self.in_scope_edit_registration:
            self.in_scope_view_registration = True

        if self.in_scope_edit_manage_waiting or \
                self.in_scope_edit_manage_accepted or \
                self.in_scope_edit_manage_attended:

            self.in_scope_view_manage = True

        # If the price is set then this MUST be visible on the user and system invoices (this one we apply silently)
        if self.price > 0:
            self.in_scope_view_user_invoice = True
            self.in_scope_view_system_invoice = True

        super(Option, self).save(*args, **kwargs)

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


class AutoSelectChoiceOption(Option):

    class Meta:
        app_label = 'events'

    auto_select_suboption = models.ForeignKey(SubOption, blank=True, null=True, default=None)


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

