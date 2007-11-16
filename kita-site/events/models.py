# coding=UTF-8

from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Create your models here.

class Event(models.Model):
    """
    Model representing an anime event
    
    """
    
    title = models.CharField(u'title', maxlength=255)
    description = models.TextField(u'description', blank=True)
    startdate = models.DateField(u'start date', blank=True, null=True)
    enddate = models.DateField(u'end date', blank=True, null=True)
    signups = models.ManyToManyField(User, filter_interface=models.HORIZONTAL, blank=True)
    registration_open = models.BooleanField(u'registration open')
    
    class Meta:
        verbose_name = u'event'
        verbose_name_plural = u'events'
    
    class Admin:
        date_hierarchy = 'startdate'
        list_display = ('title', 'registration_open')
        fields = (
            (None, { 'fields' : ('title', 'description', 'startdate', 'enddate', 'registration_open') } ), )

    def isRegistrationOpen(self):
        return self.registration_open

    def hasBeenHeld(self):
        return self.startdate < date.today()
    
    def __unicode__(self):
        return u"Event %s" % self.title
