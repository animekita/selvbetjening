
from django.db import models
from mailqueue.models import MailerMessage
from selvbetjening.core.user.models import SUser


class Log(models.Model):
    """
    Records a human readable log of changes and events in the system.

    Log messages should be usable in an audit, and should describe
    what happened and the state before and after a change.

    """

    class Meta:
        app_label = 'logging'

    # Who, where and when

    request_user = models.ForeignKey(SUser, related_name='reverse_log', null=True, blank=True)
    request_ip = models.IPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    source = models.CharField(max_length=255)

    # Do I care?

    level = models.CharField(max_length=32)

    # What

    msg = models.TextField()

    # Related to

    related_attendee = models.ForeignKey('events.Attend', related_name='log', null=True, blank=True, on_delete=models.SET_NULL)
    related_user = models.ForeignKey(SUser, related_name='log', null=True, blank=True, on_delete=models.SET_NULL)
    related_email = models.ForeignKey(MailerMessage, related_name='log', null=True, blank=True, on_delete=models.SET_NULL)