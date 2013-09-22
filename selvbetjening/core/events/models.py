# coding=UTF-8

from datetime import date, datetime

from django.contrib.auth.models import User, AnonymousUser
from django.utils.translation import ugettext as _
from django.db import models
from django.db.models.signals import post_delete, post_save, Signal
from django.utils import timezone

from selvbetjening.core.invoice.models import Invoice, Payment
from selvbetjening.core.invoice.signals import populate_invoice
from selvbetjening.core.mailcenter.sources import Source


class AttendeeAcceptPolicy(object):
    manual = 'manual'
    always = 'always'
    on_payment = 'on_payment'

    @staticmethod
    def get_choices():
        return (
            ('manual', _(u'Move attendees to accepted list manually')),
            ('on_payment', _(u'Move attendees when a payment have been made')),
            ('always', _(u'Always move to accepted list'))
        )


class Group(models.Model):
    name = models.CharField(_(u'name'), max_length=255)

    def __unicode__(self):
        return self.name


class Event(models.Model):
    group = models.ForeignKey(Group, blank=True, null=True)

    title = models.CharField(_(u'title'), max_length=255)
    description = models.TextField(_(u'description'), blank=True)

    startdate = models.DateField(_(u'start date'), blank=True, null=True)
    enddate = models.DateField(_(u'end date'), blank=True, null=True)

    # conditions
    move_to_accepted_policy = \
        models.CharField(max_length=32,
                         default=AttendeeAcceptPolicy.always,
                         choices=AttendeeAcceptPolicy.get_choices())

    maximum_attendees = models.IntegerField(_('Maximum attendees'), default=0)
    registration_open = models.BooleanField(_(u'registration open'))

    # information
    show_custom_signup_message = models.BooleanField(default=False)
    custom_signup_message = models.TextField(blank=True,
        help_text=_('The following variables are available: %s.') % u'event, user, invoice_rev, attendee')

    show_custom_change_message = models.BooleanField(default=False)
    custom_change_message = models.TextField(blank=True,
        help_text=_('The following variables are available: %s.') % u'event, user, invoice_rev, attendee')

    show_custom_status_page = models.BooleanField(default=False)
    custom_status_page = models.TextField(blank=True,
        help_text=_('The following variables are available: %s.') % u'event, user, invoice_rev, attendee')

    objects = models.Manager()

    class Translation:
        fields = ('title', 'description', 'custom_status_page')

    class Meta:
        verbose_name = _(u'event')
        verbose_name_plural = _(u'events')

    @property
    def attendees(self):
        return self.attend_set.all().order_by('id')

    @property
    def waiting_attendees(self):
        return self.attendees.filter(state=AttendState.waiting).order_by('change_timestamp', 'id')

    @property
    def accepted_attendees(self):
        return self.attendees.exclude(state=AttendState.waiting).order_by('change_timestamp', 'id')

    @property
    def optiongroups(self):
        return self.optiongroup_set.all()

    # event state
    def has_been_held(self):
        if self.enddate is None:
            return False

        return self.enddate < date.today()

    def is_registration_open(self):
        return self.registration_open and not self.has_been_held()

    def is_registration_allowed(self):
        return self.is_registration_open() and not self.max_attendees_reached()

    def has_options(self):
        return self.optiongroups.count() > 0

    # attendee management
    def add_attendee(self, user, **kwargs):
        return Attend.objects.create(user=user,
                                     event=self,
                                     **kwargs)

    def is_attendee(self, user):
        if isinstance(user, AnonymousUser):
            return False
        else:
            return self.attend_set.filter(user=user).count() == 1

    # business logic related to limitations

    def max_attendees_reached(self):
        return self.maximum_attendees != 0 and \
               self.maximum_attendees <= self.accepted_attendees.count()

    def __unicode__(self):
        return _(u'%s') % self.title


class AttendManager(models.Manager):

    def all_related(self):
        return self.all().select_related().\
            prefetch_related('invoice__payment_set').\
            prefetch_related('invoice__line_set')


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
            (AttendState.attended, _(u'Attended')),
            )


class Attend(models.Model):
    event = models.ForeignKey(Event)
    user = models.ForeignKey(User)
    invoice = models.ForeignKey(Invoice, blank=True)

    state = models.CharField(max_length=32,
                             choices=AttendState.get_choices(),
                             default=AttendState.waiting)

    is_new = models.BooleanField(default=None, blank=True)  # the correct value is set by save()

    # Updates when state changes to and from "waiting".
    # This is used when ordering the accepted and waiting attendee
    # lists. The django API can't query the attend_history
    # effectively so this is used as an alternative.
    # Please find a fix to this mess!
    change_timestamp = models.DateTimeField(null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True, null=True)

    changed = models.DateTimeField(null=True, blank=True)

    objects = AttendManager()

    class Meta:
        unique_together = ('event', 'user')
        verbose_name = _(u'attendee')
        verbose_name_plural = _(u'attendees')

    @property
    def selections(self):
        return self.selection_set.all()

    @property
    def comments(self):
        return self.comment_set.all()

    def select_option(self, option, suboption=None):
        try:
            selection = self.selection_set.get(option=option)
            selection.suboption = suboption
            selection.save()
        except Selection.DoesNotExist:
            self.selection_set.create(option=option, suboption=suboption)

    def deselect_option(self, option):
        self.selection_set.filter(option=option).delete()

    def user_first_name(self):
        return self.user.first_name
    user_first_name.admin_order_field = 'user__first_name'
    user_first_name.short_description = _('First name')

    def user_last_name(self):
        return self.user.last_name
    user_last_name.admin_order_field = 'user__last_name'
    user_last_name.short_description = _('Last name')

    @property
    def has_attended(self):
        return self.state == AttendState.attended

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

    def delete(self, *args, **kwargs):
        invoice = self.invoice
        invoice.name = _('%(event_name)s (signed off)') % {'event_name' : unicode(self.event)}
        invoice.save()

        super(Attend, self).delete(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % self.user


def update_invoice_handler_attend(sender, **kwargs):
    instance = kwargs['instance']

    try:
        instance.invoice.update()
    except Invoice.DoesNotExist:
        pass

post_delete.connect(update_invoice_handler_attend, sender=Attend)


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

    if created == True:
        attends = Attend.objects.filter(invoice=payment.invoice)
        attends = attends.filter(event__move_to_accepted_policy=AttendeeAcceptPolicy.on_payment)
        attends = attends.filter(state=AttendState.waiting)

        for attend in attends:
            attend.state = AttendState.accepted
            attend.save()

post_save.connect(update_state_on_payment, sender=Payment)

# payment keys

request_attendee_pks_signal = Signal(providing_args=['attendee'])

def basic_pks_handler(sender, **kwargs):
    attendee = kwargs['attendee']

    return ('Invoice ID', str(attendee.invoice.pk))

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

        return ('Legacy', attendee)

    except:
        return None

find_attendee_signal.connect(legacy_find_attendee_handler)


class AttendStateChange(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=32,
                             choices=AttendState.get_choices())
    attendee = models.ForeignKey(Attend, related_name='state_history')


class OptionGroup(models.Model):

    class Meta:
        ordering = ('order',)  # ordered by "order" ascending

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
    # member selected a package explictly.
    # If a user selects a package, we select all options for the user and
    # interpret this as the user selecting the package. Thus, if the user selects
    # all options, we will automatically convert this into him selecting the package.
    package_solution = models.BooleanField(default=False)
    package_price = models.DecimalField(default=0, max_digits=6, decimal_places=2)

    public_statistic = models.BooleanField(default=False)
    lock_selections_on_acceptance = models.BooleanField(default=False)

    class Translation:
        fields = ('name', 'description')

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

    group = models.ForeignKey(OptionGroup)
    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True)

    freeze_time = models.DateTimeField(_('Freeze time'), blank=True, null=True)
    maximum_attendees = models.IntegerField(_('Maximum attendees'), blank=True, null=True)

    price = models.DecimalField(default=0, max_digits=6, decimal_places=2)

    order = models.IntegerField(_('Order'), default=0)

    class Translation:
        fields = ('name', 'description')

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
    option = models.ForeignKey(Option)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2,
                                blank=True, null=True, default=None)

    class Translation:
        fields = ('name',)

    @property
    def selections(self):
        return self.selection_set.all()

    def __unicode__(self):
        return u'%s' % self.name


class Selection(models.Model):
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

# email sources

attendes_event_source = Source('attends_event_signal',
                               _(u'User registers for event'),
                               [Attend])

payment_registered_source = Source('payment_registered',
                                   _(u'Payment registered'),
                                   [Attend, Payment])


class AttendeeComment(models.Model):
    attendee = models.ForeignKey(Attend, related_name='comment_set')

    author = models.CharField(max_length=256)
    comment = models.TextField()

    timestamp = models.DateTimeField(auto_now_add=True)
