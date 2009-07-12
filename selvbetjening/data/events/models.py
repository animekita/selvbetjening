# coding=UTF-8

from datetime import date, datetime

from django.contrib.auth.models import User, AnonymousUser
from django.utils.translation import ugettext_lazy as _
from django.db import models

from selvbetjening.data.invoice.models import Invoice

class Event(models.Model):
    """ Model representing an event.

    description -- html formatted description of event
    """

    title = models.CharField(_(u'title'), max_length=255)
    description = models.TextField(_(u'description'), blank=True)
    startdate = models.DateField(_(u'start date'), blank=True, null=True)
    enddate = models.DateField(_(u'end date'), blank=True, null=True)
    maximum_attendees = models.IntegerField(_('Maximum attendees'), default=0)
    registration_open = models.BooleanField(_(u'registration open'))

    show_registration_confirmation = models.BooleanField(default=False)
    registration_confirmation = models.TextField(blank=True, help_text=_('The following variables are available: %s.') % u'event, user, invoice_rev')
    
    show_change_confirmation = models.BooleanField(default=False)
    change_confirmation = models.TextField(blank=True, help_text=_('The following variables are available: %s.') % u'event, user, invoice_rev')
    
    class Meta:
        verbose_name = _(u'event')
        verbose_name_plural = _(u'events')

    def max_attendees_reached(self):
        return self.maximum_attendees != 0 and \
               self.maximum_attendees <= self.attendees_count

    def is_registration_open(self):
        return (self.registration_open and not self.has_been_held())

    def is_registration_allowed(self):
        return self.is_registration_open() and not self.max_attendees_reached()

    def has_been_held(self):
        return self.enddate < date.today()

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

    def add_attendee(self, user, has_attended=False):
        return Attend.objects.create(user=user, has_attended=has_attended, event=self)

    def remove_attendee(self, user):
        self.attend_set.filter(user=user).delete()

    def is_attendee(self, user):
        if isinstance(user, AnonymousUser):
            return False
        else:
            return self.attend_set.filter(user=user).count() == 1

    def __unicode__(self):
        return _(u'%s') % self.title

class AttendManager(models.Manager):
    def create(self, *args, **kwargs):
        if not kwargs.has_key('invoice'):
            event = kwargs['event']
            user= kwargs['user']
            
            invoice = Invoice.objects.create(name=unicode(event),
                                             user=user,
                                             managed=True)
            
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
    def selected_options(self):
        return self.user.option_set.filter(group__event=self.event)
        
    def select_option(self, option):
        option.users.add(self.user)
        
    def deselect_option(self, option):
        option.users.remove(self.user)
        
    def update_invoice(self):
        revision = self.invoice.create_new_revision()
        for option in self.selected_options:
            revision.add_line(unicode(option), option.price)
            
        return revision
        
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
            
        self.invoice.managed = False
        self.invoice.dropped = True
        self.invoice.save()
    
    def __unicode__(self):
        return u'%s attending %s' % (self.user, self.event)

class OptionGroup(models.Model):
    event = models.ForeignKey(Event)
    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True)

    minimum_selected = models.IntegerField(_('Minimum selected'), default=0)
    maximum_selected = models.IntegerField(_('Maximum selected'), default=0)

    maximum_attendees = models.IntegerField(_('Maximum attendees'), default=0)

    freeze_time = models.DateTimeField(_('Freeze time'), blank=True, null=True)
    order = models.IntegerField(_('Order'), default=0)

    @property
    def attendees(self):
        return User.objects.filter(option__group=self.pk).distinct()

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
    users = models.ManyToManyField(User, blank=True)
    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True)

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
    def attendees(self):
        attendees = []
        for user in self.users.all():
            attendee = Attend.objects.get(event=self.group.event, user=user)
            attendees.append(attendee)
                
        return attendees
        
    @property
    def paying_attendees(self):
        paying_attendees = []
        for attendee in self.attendees:
            if attendee.invoice.is_paid():
                paying_attendees.append(attendee)
                
        return paying_attendees
    
    def attendees_count(self):
        return len(self.attendees)
    attendees_count.short_description = _('Atendees')
    
    def paying_attendees_count(self):
        return len(self.paying_attendees)

    def __unicode__(self):
        return u'%s option for %s' % (self.name, self.group)

