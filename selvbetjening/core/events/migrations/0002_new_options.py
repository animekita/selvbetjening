# coding=UTF-8

from south.db import db
from django.db import models
from selvbetjening.core.events.models import *
from django.utils.translation import ugettext_lazy as _

class Migration:

    def forwards(self, orm):

        # Adding field 'OptionGroup.freeze_time'
        db.add_column('events_optiongroup', 'freeze_time', models.DateTimeField(_('Freeze time'), null=True, blank=True))

        # Adding field 'OptionGroup.maximum_selected'
        db.add_column('events_optiongroup', 'maximum_selected', models.IntegerField(_('Maximum selected'), default=0))

        # Adding field 'OptionGroup.order'
        db.add_column('events_optiongroup', 'order', models.IntegerField(_('Order'), default=0))

        db.alter_column('events_optiongroup', 'minimum_selected', models.IntegerField(_('Minimum selected'), default=0))

        db.alter_column('events_optiongroup', 'maximum_attendees', models.IntegerField(_('Maximum attendees'), default=0))

        db.alter_column('events_option', 'order', models.IntegerField(_('Order'), default=0))

    def backwards(self, orm):

        # Deleting field 'OptionGroup.freeze_time'
        db.delete_column('events_optiongroup', 'freeze_time')

        # Deleting field 'OptionGroup.maximum_selected'
        db.delete_column('events_optiongroup', 'maximum_selected')

        # Deleting field 'OptionGroup.order'
        db.delete_column('events_optiongroup', 'order')

        db.alter_column('events_optiongrup', 'minimum_selected', models.IntegerField(_('Minimum selected')))

        db.alter_column('events_optiongroup', 'maximum_attendees', models.IntegerField(_('Maximum attendees')))

        db.alter_column('events_option', 'order', models.IntegerField(_('Order')))

    models = {

    }


