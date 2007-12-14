# coding=UTF-8
from datetime import date

from django.db import models
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
        return (self.startdate > date.today() and self.registration_open)
    
    def hasBeenHeld(self):
        return self.startdate < date.today()
    
    def __unicode__(self):
        return _(u"Event %s") % self.title
