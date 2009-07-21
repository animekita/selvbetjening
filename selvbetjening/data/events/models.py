# coding=UTF-8

from datetime import date, datetime

from django.contrib.auth.models import User, AnonymousUser
from django.utils.translation import ugettext_lazy as _
from django.db import models

from tinymce.models import HTMLField

from selvbetjening.data.invoice.models import Invoice

def _update_invoice(invoice_revision):
    invoice = invoice_revision.invoice

    for attendee in Attend.objects.filter(invoice=invoice):
        for selection in attendee.selections:
            invoice_revision.add_line(description=unicode(selection),
                                      price=selection.option.price,
                                      managed=True)

Invoice.objects.register_invoice_updater(_update_invoice)

class Event(models.Model):
    title = models.CharField(_(u'title'), max_length=255)
    description = HTMLField(_(u'description'), blank=True)

    startdate = models.DateField(_(u'start date'), blank=True, null=True)
    enddate = models.DateField(_(u'end date'), blank=True, null=True)

    maximum_attendees = models.IntegerField(_('Maximum attendees'), default=0)
    registration_open = models.BooleanField(_(u'registration open'))

    show_registration_confirmation = models.BooleanField(default=False)
    registration_confirmation = HTMLField(blank=True, help_text=_('The following variables are available: %s.') % u'event, user, invoice_rev')

    show_change_confirmation = models.BooleanField(default=False)
    change_confirmation = HTMLField(blank=True, help_text=_('The following variables are available: %s.') % u'event, user, invoice_rev')

    class Meta:
        verbose_name = _(u'event')
        verbose_name_plural = _(u'events')

    @property
    def attendees(self):
        return self.attend_set.all().order_by('id')

    @property
    def attendees_count(self):
        return self.attendees.count()

    @property
    def checkedin(self):
        return self.attendees.filter(has_attended=True)

    @property
    def checkedin_count(self):
        return self.checkedin.count()

    def max_attendees_reached(self):
        return self.maximum_attendees != 0 and \
               self.maximum_attendees <= self.attendees_count

    def is_registration_open(self):
        return (self.registration_open and not self.has_been_held())

    def is_registration_allowed(self):
        return self.is_registration_open() and not self.max_attendees_reached()

    def has_options(self):
        return self.optiongroup_set.count() > 0

    def has_been_held(self):
        return self.enddate < date.today()

    def add_attendee(self, user, has_attended=False):
        return Attend.objects.create(user=user,
                                     has_attended=has_attended,
                                     event=self)

    def remove_attendee(self, user):
        self.attend_set.get(user=user).delete()

    def is_attendee(self, user):
        if isinstance(user, AnonymousUser):
            return False
        else:
            return self.attend_set.filter(user=user).count() == 1

    def __unicode__(self):
        return _(u'%s') % self.title

class AttendManager(models.Manager):
    def create(self, *args, **kwargs):
        if kwargs.has_key('invoice'):
            invoice = kwargs['invoice']
        else:
            invoice = Invoice.objects.create(name=unicode(kwargs['event']),
                                             user=kwargs['user'])

            kwargs['invoice'] = invoice

        return super(AttendManager, self).create(*args, **kwargs)

class Attend(models.Model):
    event = models.ForeignKey(Event)
    user = models.ForeignKey(User)
    invoice = models.ForeignKey(Invoice, blank=True)
    has_attended = models.BooleanField()

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

    def change_selections(self, selections, deselections):
        for option, suboption in selections:
            self.select_option(option, suboption)
        for option in deselections:
            self.deselect_option(option)

    def is_new(self):
        return self.user.attend_set.filter(event__startdate__lt=self.event.startdate).filter(has_attended=True).count() == 0
    is_new.boolean = True

    def user_first_name(self):
        # Stupid function, but needed by the django admin interface
        # to show sortable user information from the attend administration.
        return self.user.first_name
    user_first_name.admin_order_field = 'user__first_name'
    user_first_name.short_description = _('First name')

    def user_last_name(self):
        # See description for user_first_name
        return self.user.last_name
    user_last_name.admin_order_field = 'user__last_name'
    user_last_name.short_description = _('Last name')

    def delete(self):
        for option in Option.objects.filter(group__event=self.event):
            self.deselect_option(option)

        invoice = self.invoice

        super(Attend, self).delete()

        invoice.update()

    def __unicode__(self):
        return u'%s attending %s' % (self.user, self.event)

class OptionGroup(models.Model):
    event = models.ForeignKey(Event)
    name = models.CharField(_('Name'), max_length=255)
    description = HTMLField(_('Description'), blank=True)

    minimum_selected = models.IntegerField(_('Minimum selected'), default=0)
    maximum_selected = models.IntegerField(_('Maximum selected'), default=0)

    maximum_attendees = models.IntegerField(_('Maximum attendees'), default=0)

    freeze_time = models.DateTimeField(_('Freeze time'), blank=True, null=True)
    order = models.IntegerField(_('Order'), default=0)

    @property
    def attendees(self):
        return Attend.objects.filter(selection__option__group=self.pk).distinct()

    def attendees_count(self):
        return self.attendees.count()
    attendees_count.short_description = _('Atendees')

    def is_frozen(self):
        if self.freeze_time is None:
            return False
        else:
            return datetime.now() > self.freeze_time

    def max_attendees_reached(self):
        return self.maximum_attendees > 0 and self.attendees_count() >= self.maximum_attendees

    def __unicode__(self):
        return u'%s: %s' % (self.event.title, self.name)

class Option(models.Model):
    group = models.ForeignKey(OptionGroup)
    name = models.CharField(_('Name'), max_length=255)
    description = HTMLField(_('Description'), blank=True)

    freeze_time = models.DateTimeField(_('Freeze time'), blank=True, null=True)
    maximum_attendees = models.IntegerField(_('Maximum attendees'), blank=True, null=True)

    price = models.IntegerField(default=0)

    order = models.IntegerField(_('Order'), default=0)

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
           self.attendees_count() >= self.maximum_attendees:
            return True
        else:
            return False

    @property
    def selections(self):
        return self.selection_set.all()

    @property
    def paid_selections(self):
        paid_selections = []
        for selection in self.selections:
            if selection.attendee.invoice.is_paid():
                paid_selections.append(selection)

        return paid_selections

    def attendee_count(self):
        return self.selections.count()
    attendee_count.short_description = _('Attendees')

    def paid_selections_count(self):
        return len(self.paid_selections)

    def __unicode__(self):
        return u'%s option for %s' % (self.name, self.group)

class SubOption(models.Model):
    option = models.ForeignKey(Option)
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return u'%s' % self.name

class Selection(models.Model):
    attendee = models.ForeignKey(Attend)
    option = models.ForeignKey(Option)
    suboption = models.ForeignKey(SubOption, blank=True, null=True)

    class Meta:
        unique_together = (('attendee', 'option'))

    def __unicode__(self):
        return unicode(self.option)