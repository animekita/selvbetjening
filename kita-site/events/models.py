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
    signups = models.ManyToManyField(User, filter_interface=models.HORIZONTAL, blank=True)
    registration_open = models.BooleanField(_(u"registration open"))
    
    class Meta:
        verbose_name = _(u"event")
        verbose_name_plural = _(u"events")
    
    class Admin:
        date_hierarchy = 'startdate'
        list_display = ('title', 'registration_open')
        fields = (
            (None, { 'fields' : ('title', 'description', 'startdate', 'enddate', 'registration_open') } ), )

    def isRegistrationOpen(self):
        return (self.registration_open and not self.hasBeenHeld())
    
    def hasBeenHeld(self):
        return self.startdate < date.today()
    
    def get_guests(self):
        cursor = connection.cursor()
        cursor.execute("SELECT user.id as id, user.username as username, user.first_name as first_name, user.last_name as last_name FROM auth_user as user, events_event_signups as signups WHERE user.id=signups.user_id AND signups.event_id=%s ORDER BY signups.id ASC", [self.id])
        return cursor.fetchall()
    
    def __unicode__(self):
        return _(u"Event %s") % self.title
