# coding=UTF-8

from south.db import db
from django.db import models
from selvbetjening.events.models import *
from django.utils.translation import ugettext_lazy as _

class Migration:

    def forwards(self, orm):

        # Adding field 'events_event.maximum_attendees'
        db.add_column('events_event', 'maximum_attendees', models.IntegerField(_('Maximum attendees'), default=0))

    def backwards(self, orm):

        # Deleting field 'OptionGroup.freeze_time'
        db.delete_column('events_event', 'maximum_attendees')

    models = {

    }


