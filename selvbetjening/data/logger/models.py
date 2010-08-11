from django.db import models
from django.contrib.auth.models import User

from selvbetjening.data.events.models import Event

class Entry(models.Model):
    message = models.CharField(max_length=255)

    # message identification
    module = models.CharField(max_length=32)
    category = models.CharField(max_length=32)

    # meta
    timestamp = models.DateTimeField(auto_now_add=True)

    # related (extracted from request)
    ip = models.CharField(max_length=15, blank=True)
    user = models.ForeignKey(User, blank=True, null=True)

    # related (given as argument)
    event = models.ForeignKey(Event, blank=True, null=True)

class SavedLog(models.Model):
    key = models.CharField(max_length=32)
    query = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)