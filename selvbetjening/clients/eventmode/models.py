from datetime import date

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from selvbetjening.data.events.models import Event

class EventmodeMachineManager(models.Manager):
    def authenticate(self, event, passphrase):
        """ Authenticate passphrase, returning matching EventmodeMachine """

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
    name -- name identifying the machine
    passphrase -- sha1 hashed passphrase
    active -- boolean declaring if the machine is active (can login)
    """

    event = models.ForeignKey(Event)
    name = models.CharField(max_length=255)
    passphrase = models.CharField(max_length=255)
    active = models.BooleanField(default=False)

    objects = EventmodeMachineManager()

    class Meta:
        unique_together = ('event', 'passphrase')

    def is_valid(self):
        return self.active
