# coding=UTF-8

from datetime import date, datetime

from django.contrib.auth.models import User, AnonymousUser
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models.signals import post_delete, post_save, pre_delete, pre_save
from django.core.cache import cache

from tinymce.models import HTMLField

from selvbetjening.data.invoice.models import Invoice
from selvbetjening.data.invoice.signals import populate_invoice

class AttendeeAcceptPolicy(object):
    manual = 'manual'
    always = 'always'

    @staticmethod
    def get_choices():
        return (
            ('manual', _(u'Move attendees to accepted list manually')),
            ('on_payment', _(u'Move attendees when a payment have been made')),
            ('always', _(u'Always move to accepted list'))
        )

class Event(models.Model):
    _CACHED_OPTIONGROUPS_ID = 'event-%d-optiongroups'
    _CACHED_ATTENDEES_ID = 'event-%d-attendees'
    _CACHED_ACCEPTED_ATTENDEES_ID = 'event-%d-accepted-attendees'

    title = models.CharField(_(u'title'), max_length=255)
    description = HTMLField(_(u'description'), blank=True)

    startdate = models.DateField(_(u'start date'), blank=True, null=True)
    enddate = models.DateField(_(u'end date'), blank=True, null=True)

    # conditions
    move_to_accepted_policy = \
        models.CharField(max_length=32,
                         default=AttendeeAcceptPolicy.always,
                         choices=AttendeeAcceptPolicy.get_choices())

    maximum_attendees = models.IntegerField(_('Maximum attendees'), default=0)
    registration_open = models.BooleanField(_(u'registration open'))

    show_registration_confirmation = models.BooleanField(default=False)
    registration_confirmation = HTMLField(blank=True, help_text=_('The following variables are available: %s.') % u'event, user, invoice_rev')

    # information
    show_change_confirmation = models.BooleanField(default=False)
    change_confirmation = HTMLField(blank=True, help_text=_('The following variables are available: %s.') % u'event, user, invoice_rev')

    show_invoice_page = models.BooleanField(default=False)
    invoice_page = HTMLField(blank=True, help_text=_('The following variables are available: %s.') % u'event, user, invoice_rev')

    objects = models.Manager()

    class Translation:
        fields = ('title', 'description')

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
    def accepted_attendees(self):
        cid = self._CACHED_ATTENDEES_ID % self.pk
        attendees = cache.get(cid)

        if attendees is None:
            attendees = self.attendees.exclude(state=AttendState.waiting)
            cache.set(cid, attendees)

        return attendees

    @property
    def optiongroups(self):
        cid = self._CACHED_OPTIONGROUPS_ID % self.pk
        optiongroups = cache.get(cid)

        if optiongroups is None:
            optiongroups = self.optiongroup_set.all()
            cache.set(cid, optiongroups)

        return optiongroups

    # event state
    def has_been_held(self):
        return self.enddate < date.today()

    def is_registration_open(self):
        return (self.registration_open and not self.has_been_held())

    def is_registration_allowed(self):
        return self.is_registration_open() and not self.max_attendees_reached()

    def has_options(self):

        return self.optiongroup_set.count() > 0

    # attendee management
    def add_attendee(self, user, **kwargs):
        return Attend.objects.create(user=user,
                                     event=self,
                                     **kwargs)

    def remove_attendee(self, user):
        self.attend_set.get(user=user).delete()

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

def delete_event_caches(sender, **kwargs):
    pass

pre_delete.connect(delete_event_caches, sender=Event)
post_save.connect(delete_event_caches, sender=Event)

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


    objects = AttendManager()

    class Meta:
        unique_together = ('event', 'user')

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
        if self.event.move_to_accepted_policy == AttendeeAcceptPolicy.always:
            self.state = AttendState.accepted

        super(Attend, self).save(*args, **kwargs)

    def delete(self):
        invoice = self.invoice
        invoice.name = _('%(event_name)s (signed off)') % {'event_name' : unicode(self.event)}
        invoice.save()

        super(Attend, self).delete()

    def __unicode__(self):
        return u'%s attending %s' % (self.user, self.event)

def delete_event_attendees_cache(sender, **kwargs):
    instance = kwargs['instance']
    cache.delete(Event._CACHED_ATTENDEES_ID % instance.event.pk)
    cache.delete(Event._CACHED_ACCEPTED_ATTENDEES_ID % instance.event.pk)

pre_delete.connect(delete_event_attendees_cache, sender=Attend)
post_save.connect(delete_event_attendees_cache, sender=Attend)

def update_invoice_with_attend_handler(sender, **kwargs):
    invoice_revision = kwargs['invoice_revision']
    invoice = invoice_revision.invoice

    for attendee in Attend.objects.filter(invoice=invoice):
        for selection in attendee.selections:
            invoice_revision.add_line(description=unicode(selection),
                                      price=selection.option.price,
                                      managed=True)

populate_invoice.connect(update_invoice_with_attend_handler)

class OptionGroup(models.Model):
    _CACHED_OPTIONS_ID = 'optiongroup-%d-options'

    event = models.ForeignKey(Event)
    name = models.CharField(_('Name'), max_length=255)
    description = HTMLField(_('Description'), blank=True)

    minimum_selected = models.IntegerField(_('Minimum selected'), default=0)
    maximum_selected = models.IntegerField(_('Maximum selected'), default=0)

    maximum_attendees = models.IntegerField(_('Maximum attendees'), default=0)

    freeze_time = models.DateTimeField(_('Freeze time'), blank=True, null=True)
    order = models.IntegerField(_('Order'), default=0)

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
            options = self.option_set.order_by('order')
            cache.set(cid, options)

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
        return u'%s: %s' % (self.event.title, self.name)

def delete_optiongroup_caches(sender, **kwargs):
    instance = kwargs['instance']
    cache.delete(Event._CACHED_OPTIONGROUPS_ID % instance.event.pk)
    cache.delete(OptionGroup._CACHED_OPTIONS_ID % instance.pk)

pre_delete.connect(delete_optiongroup_caches, sender=OptionGroup)
post_save.connect(delete_optiongroup_caches, sender=OptionGroup)

class Option(models.Model):
    group = models.ForeignKey(OptionGroup)
    name = models.CharField(_('Name'), max_length=255)
    description = HTMLField(_('Description'), blank=True)

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
        return u'%s' % self.name

class SubOption(models.Model):
    option = models.ForeignKey(Option)
    name = models.CharField(max_length=255)

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

    class Meta:
        unique_together = (('attendee', 'option'))

    def __unicode__(self):
        if self.suboption:
            return u'%s (%s)' % (self.option, self.suboption)
        else:
            return u'%s' % self.option

def update_invoice_handler(sender, **kwargs):
    instance = kwargs['instance']
    instance.attendee.invoice.update()

post_delete.connect(update_invoice_handler, sender=Selection)
post_save.connect(update_invoice_handler, sender=Selection)