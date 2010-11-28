# coding=UTF-8

from south.db import db
from django.db import models
from selvbetjening.core.events.models import *

class Migration:

    def forwards(self, orm):

        # Adding model 'SubOption'
        db.create_table('events_suboption', (
            ('id', models.AutoField(primary_key=True)),
            ('name', models.TextField(max_length=255)),
            ('option', models.ForeignKey(orm.Option)),
        ))
        db.send_create_signal('events', ['SubOption'])

        # Adding model 'Selection'
        db.create_table('events_selection', (
            ('attendee', models.ForeignKey(orm.Attend)),
            ('suboption', models.ForeignKey(orm.SubOption, null=True, blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('option', models.ForeignKey(orm.Option)),
        ))
        db.send_create_signal('events', ['Selection'])

        # Creating unique_together for [attendee, option] on Selection.
        db.create_unique('events_selection', ['attendee_id', 'option_id'])

    def backwards(self, orm):

        # Deleting model 'SubOption'
        db.delete_table('events_suboption')

        # Deleting model 'Selection'
        db.delete_table('events_selection')

        # Deleting unique_together for [attendee, option] on Selection.
        db.delete_unique('events_selection', ['attendee_id', 'option_id'])



    models = {
        'events.event': {
            'change_confirmation': ('models.TextField', [], {'blank': 'True'}),
            'description': ('models.TextField', ["_(u'description')"], {'blank': 'True'}),
            'enddate': ('models.DateField', ["_(u'end date')"], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'maximum_attendees': ('models.IntegerField', ["_('Maximum attendees')"], {'default': '0'}),
            'registration_confirmation': ('models.TextField', [], {'blank': 'True'}),
            'registration_open': ('models.BooleanField', ["_(u'registration open')"], {}),
            'show_change_confirmation': ('models.BooleanField', [], {'default': 'False'}),
            'show_registration_confirmation': ('models.BooleanField', [], {'default': 'False'}),
            'startdate': ('models.DateField', ["_(u'start date')"], {'null': 'True', 'blank': 'True'}),
            'title': ('models.CharField', ["_(u'title')"], {'max_length': '255'})
        },
        'events.suboption': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.TextField', [], {'max_length': '255'}),
            'option': ('models.ForeignKey', ['Option'], {})
        },
        'events.attend': {
            'Meta': {'unique_together': "('event','user')"},
            'event': ('models.ForeignKey', ['Event'], {}),
            'has_attended': ('models.BooleanField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('models.ForeignKey', ['Invoice'], {'blank': 'True'}),
            'user': ('models.ForeignKey', ['User'], {})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'invoice.invoice': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'events.selection': {
            'Meta': {'unique_together': "(('attendee','option'))"},
            'attendee': ('models.ForeignKey', ['Attend'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'option': ('models.ForeignKey', ['Option'], {}),
            'suboption': ('models.ForeignKey', ['SubOption'], {'null': 'True', 'blank': 'True'})
        },
        'events.optiongroup': {
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'event': ('models.ForeignKey', ['Event'], {}),
            'freeze_time': ('models.DateTimeField', ["_('Freeze time')"], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'maximum_attendees': ('models.IntegerField', ["_('Maximum attendees')"], {'default': '0'}),
            'maximum_selected': ('models.IntegerField', ["_('Maximum selected')"], {'default': '0'}),
            'minimum_selected': ('models.IntegerField', ["_('Minimum selected')"], {'default': '0'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '255'}),
            'order': ('models.IntegerField', ["_('Order')"], {'default': '0'})
        },
        'events.option': {
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'freeze_time': ('models.DateTimeField', ["_('Freeze time')"], {'null': 'True', 'blank': 'True'}),
            'group': ('models.ForeignKey', ['OptionGroup'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'maximum_attendees': ('models.IntegerField', ["_('Maximum attendees')"], {'null': 'True', 'blank': 'True'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '255'}),
            'order': ('models.IntegerField', ["_('Order')"], {'default': '0'}),
            'price': ('models.IntegerField', [], {'default': '0'}),
            'users': ('models.ManyToManyField', ['User'], {'blank': 'True'})
        }
    }

    complete_apps = ['events']
