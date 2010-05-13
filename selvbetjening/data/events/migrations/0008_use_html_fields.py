# coding=UTF-8

from south.db import db
from django.db import models
from selvbetjening.data.events.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Changing field 'Event.description'
        db.alter_column('events_event', 'description', models.TextField(_(u'description'), blank=True))
        
        # Changing field 'Event.registration_confirmation'
        db.alter_column('events_event', 'registration_confirmation', models.TextField(blank=True))
        
        # Changing field 'Event.change_confirmation'
        db.alter_column('events_event', 'change_confirmation', models.TextField(blank=True))
        
        # Changing field 'Option.description'
        db.alter_column('events_option', 'description', models.TextField(_('Description'), blank=True))
        
        # Changing field 'OptionGroup.description'
        db.alter_column('events_optiongroup', 'description', models.TextField(_('Description'), blank=True))
        
    
    
    def backwards(self, orm):
        
        # Changing field 'Event.description'
        db.alter_column('events_event', 'description', models.TextField(_(u'description'), blank=True))
        
        # Changing field 'Event.registration_confirmation'
        db.alter_column('events_event', 'registration_confirmation', models.TextField(blank=True))
        
        # Changing field 'Event.change_confirmation'
        db.alter_column('events_event', 'change_confirmation', models.TextField(blank=True))
        
        # Changing field 'Option.description'
        db.alter_column('events_option', 'description', models.TextField(_('Description'), blank=True))
        
        # Changing field 'OptionGroup.description'
        db.alter_column('events_optiongroup', 'description', models.TextField(_('Description'), blank=True))
        
    
    
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
