from datetime import date
import hashlib

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from selvbetjening.events.models import Event

class EventmodeMachineManager(models.Manager):
    def authenticate(self, event, passphrase):
        """ Authenticate passphrase, returning matching EventmodeMachine """
        passhash = hashlib.sha1(passphrase).hexdigest()

        try:
            eventmode = self.get(passphrase=passphrase, event=event)
            if eventmode.is_valid():
                return eventmode
        except ObjectDoesNotExist:
            return None

        return None

class EventmodeMachine(models.Model):
    """
    Model representing a physical machine used at a event.

    event -- associated event
    name -- name identifying
    passphrase - sha1 hashed passphrase
    """

    event = models.ForeignKey(Event)
    name = models.CharField(max_length=255)
    passphrase = models.CharField(max_length=255)


    objects = EventmodeMachineManager()

    class Meta:
        unique_together = ('event', 'passphrase')

    def is_valid(self):
        return (self.event.enddate >= date.today() and self.event.startdate <= date.today())
