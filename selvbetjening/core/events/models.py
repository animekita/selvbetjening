# coding=UTF-8

from datetime import date, datetime

from django.contrib.auth.models import User, AnonymousUser
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models.signals import post_delete, post_save, pre_delete, pre_save, Signal
from django.core.cache import cache

from selvbetjening.core.invoice.models import Invoice, Payment
from selvbetjening.core.invoice.signals import populate_invoice
from selvbetjening.core.mailcenter.sources import Source

import processors

_EVENT_CACHE_IDS = []

def purge_cache():
    global _EVENT_CACHE_IDS
    for cid in _EVENT_CACHE_IDS:
        cache.delete(cid)

    _EVENT_CACHE_IDS = []

def delete_caches_on_event_change(sender, **kwargs):
    purge_cache()

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
    _CACHED_OPTIONGROUPS_ID = 'event-%d-optiongroups'
    _CACHED_ATTENDEES_ID = 'event-%d-attendees'
    _CACHED_ACCEPTED_ATTENDEES_ID = 'event-%d-accepted-attendees'
    _CACHED_WAITING_ATTENDEES_ID = 'event-%d-waiting-attendees'

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

    # cache related sets
    @property
    def attendees(self):
        cid = self._CACHED_ATTENDEES_ID % self.pk
        attendees = cache.get(cid)

        if attendees is None:
            attendees = self.attend_set.all().order_by('id')
            cache.set(cid, attendees)

        return attendees

    @property
    def waiting_attendees(self):
        cid = self._CACHED_WAITING_ATTENDEES_ID % self.pk
        attendees = cache.get(cid)

        if attendees is None:
            attendees = self.attendees.filter(state=AttendState.waiting).order_by('change_timestamp', 'id')
            cache.set(cid, attendees)

        return attendees

    @property
    def accepted_attendees(self):
        cid = self._CACHED_ACCEPTED_ATTENDEES_ID % self.pk
        attendees = cache.get(cid)

        if attendees is None:
            attendees = self.attendees.exclude(state=AttendState.waiting).order_by('change_timestamp', 'id')
            cache.set(cid, attendees)

        return attendees

    @property
    def optiongroups(self):
        cid = self._CACHED_OPTIONGROUPS_ID % self.pk
        optiongroups = cache.get(cid)

        if optiongroups is None:
            optiongroups = self.optiongroup_set.all()
            cache.set(cid, optiongroups)
            _EVENT_CACHE_IDS.append(cid)

        return optiongroups

    # event state
    def has_been_held(self):
        if self.enddate is None:
            return False

        return self.enddate < date.today()

    def is_registration_open(self):
        return (self.registration_open and not self.has_been_held())

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

pre_delete.connect(delete_caches_on_event_change, sender=Event)
post_save.connect(delete_caches_on_event_change, sender=Event)

class AttendManager(models.Manager):
    def create(self, *args, **kwargs):
        if kwargs.has_key('invoice'):
            invoice = kwargs['invoice']
        else:
            invoice = Invoice.objects.create(name=unicode(kwargs['event']),
                                             user=kwargs['user'])

            kwargs['invoice'] = invoice

        return super(AttendManager, self).create(*args, **kwargs)

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

    # Updates when state changes to and from "waiting".
    # This is used when ordering the accepted and waiting attendee
    # lists. The django API can't query the attend_history
    # effectively so this is used as an alternative.
    # Please find a fix to this mess!
    change_timestamp = models.DateTimeField(null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True, null=True)

    objects = AttendManager()

    class Meta:
        unique_together = ('event', 'user')
        verbose_name = _(u'attendee')
        verbose_name_plural = _(u'attendees')

    @property
    def selections(self):
        return self.selection_set.all()

    def select_option(self, option, suboption=None):
        try:
            selection = self.selection_set.get(option=option)
            selection.suboption = suboption
            selection.save()
        except Selection.DoesNotExist:
            self.selection_set.create(option=option, suboption=suboption)

    def deselect_option(self, option):
        self.selection_set.filter(option=option).delete()

    def is_new(self):
        if self.event.startdate is None:
            return False
        
        return self.user.attend_set.filter(event__startdate__lt=self.event.startdate).filter(state=AttendState.attended).count() == 0
    is_new.boolean = True

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


    def delete(self):
        invoice = self.invoice
        invoice.name = _('%(event_name)s (signed off)') % {'event_name' : unicode(self.event)}
        invoice.save()

        super(Attend, self).delete()

    def __unicode__(self):
        return u'%s' % self.user

def delete_event_attendees_cache(sender, **kwargs):
    instance = kwargs['instance']
    cache.delete(Event._CACHED_ATTENDEES_ID % instance.event.pk)
    cache.delete(Event._CACHED_ACCEPTED_ATTENDEES_ID % instance.event.pk)
    cache.delete(Event._CACHED_WAITING_ATTENDEES_ID % instance.event.pk)

pre_delete.connect(delete_event_attendees_cache, sender=Attend)
post_save.connect(delete_event_attendees_cache, sender=Attend)

def update_invoice_handler_attend(sender, **kwargs):
    instance = kwargs['instance']
    
    try: 
        instance.invoice.update()
    except Invoice.DoesNotExist:
        pass

post_delete.connect(update_invoice_handler_attend, sender=Attend)

def update_invoice_with_attend_handler(sender, **kwargs):
    invoice_revision = kwargs['invoice_revision']
    invoice = invoice_revision.invoice

    for attendee in Attend.objects.filter(invoice=invoice):
        for selection in attendee.selections:
            invoice_revision.add_line(description=unicode(selection),
                                      price=selection.price,
                                      managed=True)

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

    return ('Legacy ID', key)

request_attendee_pks_signal.connect(legacy_attendee_pks_handler)

find_attendee_signal = Signal(providing_args=['pk'])

def basic_find_attendee_handler(sender, **kwargs):
    try:
        pk = int(kwargs['pk'])
        return ('Invoice ID', Attend.objects.get(pk=pk))

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
    _CACHED_OPTIONS_ID = 'optiongroup-%d-options'

    event = models.ForeignKey(Event)
    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True)

    minimum_selected = models.IntegerField(_('Minimum selected'), default=0)
    maximum_selected = models.IntegerField(_('Maximum selected'), default=0)

    maximum_attendees = models.IntegerField(_('Maximum attendees'), default=0)

    freeze_time = models.DateTimeField(_('Freeze time'), blank=True, null=True)
    order = models.IntegerField(_('Order'), default=0)

    public_statistic = models.BooleanField(default=False)
    lock_selections_on_acceptance = models.BooleanField(default=False)

    class Translation:
        fields = ('name', 'description')

    # cached related sets
    @property
    def attendees(self):
        return Attend.objects.filter(selection__option__group=self.pk).distinct()

    @property
    def accepted_attendees(self):
        return self.attendees.exclude(state=AttendState.waiting)

    @property
    def options(self):
        cid = self._CACHED_OPTIONS_ID % self.pk
        options = cache.get(cid)

        if options is None:
            options = self.option_set.select_related().order_by('order')
            cache.set(cid, options)
            _EVENT_CACHE_IDS.append(cid)

        return options

    def is_frozen(self):
        if self.freeze_time is None:
            return False
        else:
            return datetime.now() > self.freeze_time

    # business logic related to limitations

    def max_attendees_reached(self):
        return self.maximum_attendees > 0 and self.accepted_attendees.count() >= self.maximum_attendees

    def __unicode__(self):
        return u'%s' % self.name

pre_delete.connect(delete_caches_on_event_change, sender=OptionGroup)
post_save.connect(delete_caches_on_event_change, sender=OptionGroup)

class Option(models.Model):
    _CACHED_OPTION_SUBOPTIONS_ID = 'option-%d-suboptions'

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
        cid = self._CACHED_OPTION_SUBOPTIONS_ID % self.pk
        suboptions = cache.get(cid)

        if suboptions is None:
            suboptions = self.suboption_set.all()
            cache.set(cid, suboptions)
            _EVENT_CACHE_IDS.append(cid)

        return suboptions

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

pre_delete.connect(delete_caches_on_event_change, sender=SubOption)
post_save.connect(delete_caches_on_event_change, sender=SubOption)

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