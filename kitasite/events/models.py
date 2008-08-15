# coding=UTF-8
from datetime import date, datetime

from django.db import models, connection
from django.contrib.auth.models import User, AnonymousUser
from datetime import date
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class Event(models.Model):
    """
    Model representing an anime event

    """

    title = models.CharField(_(u"title"), max_length=255)
    description = models.TextField(_(u"description"), blank=True)
    startdate = models.DateField(_(u"start date"), blank=True, null=True)
    enddate = models.DateField(_(u"end date"), blank=True, null=True)
    registration_open = models.BooleanField(_(u"registration open"))

    class Meta:
        verbose_name = _(u"event")
        verbose_name_plural = _(u"events")

    class Admin:
        date_hierarchy = 'startdate'
        list_display = ('title', 'registration_open')
        fields = (
            (None, { 'fields' : ('title', 'description', 'startdate', 'enddate', 'registration_open') } ), )

    def is_registration_open(self):
        return (self.registration_open and not self.has_been_held())

    def has_been_held(self):
        return self.enddate < date.today()

    def get_attendees(self):
        return self.attend_set.all().order_by('id')

    def add_attendee(self, user, has_attended=False):
        Attend.objects.create(user=user, has_attended=has_attended, event=self)

    def remove_attendee(self, user):
        self.attend_set.filter(user=user).delete()
        for option in Option.objects.filter(group__event=self):
            option.users.remove(user)

    def is_attendee(self, user):
        if isinstance(user, AnonymousUser):
            return False
        else:
            return (len(self.attend_set.filter(user=user)) == 1)

    def __unicode__(self):
        return _(u"Event %s") % self.title

class Attend(models.Model):

    event = models.ForeignKey(Event)
    user = models.ForeignKey(User)
    has_attended = models.BooleanField()

class OptionGroup(models.Model):
    event = models.ForeignKey(Event)
    name = models.CharField(_('Name'), max_length=255)
    description = models.CharField(_('Description'), max_length=255, blank=True)
    minimum_selected = models.IntegerField(_('Minimum selected'))

    def __unicode__(self):
        return u'%s: %s' % (self.event.title, self.name)

class Option(models.Model):
    group = models.ForeignKey(OptionGroup)
    users = models.ManyToManyField(User, blank=True)
    name = models.CharField(_('Name'), max_length=255)
    description = models.CharField(_('Description'), max_length=255, blank=True)
    freeze_time = models.DateTimeField(_('Freeze time'), blank=True, null=True)
    order = models.IntegerField(_('Order'))

    def is_frozen(self):
        if self.freeze_time is None:
            return False
        else:
            return datetime.now() > self.freeze_time

    def count(self):
        return self.users.count()
    count.short_description = _('Atendees')

    class Admin:
        list_display = ('event', 'description', 'order')
        fields = (
            (None, { 'fields' : ('description', 'order', 'event') } ), )

