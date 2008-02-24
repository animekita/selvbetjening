# coding=UTF-8
from datetime import date

from django.db import models, connection
from django.contrib.auth.models import User
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
        return self.startdate < date.today()
    
    def get_attendees(self):
        return self.attend_set.all().order_by('id')
    
    def add_attendee(self, user, has_attended=False):
        Attend.objects.create(user=user, has_attended=has_attended, event=self)
    
    def remove_attendee(self, user):
        self.attend_set.filter(user=user).delete()
        for option in self.option_set.all():
            option.users.remove(user)
    
    def is_attendee(self, user):
        return (len(self.attend_set.filter(user=user)) == 1)
    
    def __unicode__(self):
        return _(u"Event %s") % self.title

class Attend(models.Model):
    
    event = models.ForeignKey(Event)
    user = models.ForeignKey(User)
    has_attended = models.BooleanField()

class Option(models.Model):
    event = models.ForeignKey(Event)
    users = models.ManyToManyField(User, blank=True)
    description = models.CharField(_('Description'), max_length=255)
    order = models.IntegerField(_('Order'))
    
    def count(self):
        return len(self.users.all())
    
    class Admin:
        list_display = ('event', 'description', 'order')
        fields = (
            (None, { 'fields' : ('description', 'order', 'event') } ), )
    
    