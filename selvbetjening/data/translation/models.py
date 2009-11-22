from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings

class Translation(models.Model):
    LOCALE_CHOICES = [lang for lang in settings.LANGUAGES if lang[0] != settings.LANGUAGE_CODE]

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    translated_object = generic.GenericForeignKey('content_type', 'object_id')

    field = models.CharField(max_length=64)

    locale = models.CharField(max_length=8, choices=LOCALE_CHOICES)
    translation = models.TextField()