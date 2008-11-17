from datetime import date

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from selvbetjening.events.models import Event

class EventmodeManager(models.Manager):
    def check_passphrase(self, passphrase):
        try:
            eventmode = self.get(passphrase=passphrase)
            return eventmode.is_valid()
        except ObjectDoesNotExist:
            return False

class Eventmode(models.Model):
    event = models.ForeignKey(Event)
    passphrase = models.CharField(max_length=255, unique=True)

    objects = EventmodeManager()

    def is_valid(self):
        return (self.event.enddate >= date.today() and self.event.startdate <= date.today())

    class Admin:
        pass
