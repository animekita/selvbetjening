# coding=UTF-8

from south.db import db
from django.db import models
from selvbetjening.core.events.models import *

class Migration:

    def forwards(self, orm):

        # Adding model 'AttendStateChange'
        db.create_table('events_attendstatechange', (
            ('id', orm['events.attendstatechange:id']),
            ('timestamp', orm['events.attendstatechange:timestamp']),
            ('state', orm['events.attendstatechange:state']),
            ('attendee', orm['events.attendstatechange:attendee']),
        ))
        db.send_create_signal('events', ['AttendStateChange'])

        # Adding field 'Attend.registration_date'
        db.add_column('events_attend', 'registration_date', orm['events.attend:registration_date'])

        # Changing field 'Event.registration_confirmation'
        # (to signature: django.db.models.fields.TextField(blank=True))
        #db.alter_column('events_event', 'registration_confirmation', orm['events.event:registration_confirmation'])

        # Changing field 'Event.invoice_page'
        # (to signature: django.db.models.fields.TextField(blank=True))
        #db.alter_column('events_event', 'invoice_page', orm['events.event:invoice_page'])

        # Changing field 'Event.change_confirmation'
        # (to signature: django.db.models.fields.TextField(blank=True))
        #db.alter_column('events_event', 'change_confirmation', orm['events.event:change_confirmation'])



    def backwards(self, orm):

        # Deleting model 'AttendStateChange'
        db.delete_table('events_attendstatechange')

        # Deleting field 'Attend.registration_date'
        db.delete_column('events_attend', 'registration_date')

        # Changing field 'Event.registration_confirmation'
        # (to signature: models.TextField(blank=True))
        db.alter_column('events_event', 'registration_confirmation', orm['events.event:registration_confirmation'])

        # Changing field 'Event.invoice_page'
        # (to signature: models.TextField(blank=True))
        db.alter_column('events_event', 'invoice_page', orm['events.event:invoice_page'])

        # Changing field 'Event.change_confirmation'
        # (to signature: models.TextField(blank=True))
        db.alter_column('events_event', 'change_confirmation', orm['events.event:change_confirmation'])



    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'events.attend': {
            'Meta': {'unique_together': "(('event', 'user'),)"},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['invoice.Invoice']", 'blank': 'True'}),
            'registration_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'waiting'", 'max_length': '32'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'events.attendstatechange': {
            'attendee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'state_history'", 'to': "orm['events.Attend']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'events.event': {
            'change_confirmation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('models.TextField', ["_(u'description')"], {'blank': 'True'}),
            'enddate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_page': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'maximum_attendees': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'move_to_accepted_policy': ('django.db.models.fields.CharField', [], {'default': "'always'", 'max_length': '32'}),
            'registration_confirmation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'registration_open': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'show_change_confirmation': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'show_invoice_page': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'show_registration_confirmation': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'startdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'events.option': {
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'freeze_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.OptionGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum_attendees': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'})
        },
        'events.optiongroup': {
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Event']"}),
            'freeze_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum_attendees': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'maximum_selected': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'minimum_selected': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'events.selection': {
            'Meta': {'unique_together': "(('attendee', 'option'),)"},
            'attendee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Attend']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Option']"}),
            'suboption': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.SubOption']", 'null': 'True', 'blank': 'True'})
        },
        'events.suboption': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Option']"})
        },
        'invoice.invoice': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['events']
