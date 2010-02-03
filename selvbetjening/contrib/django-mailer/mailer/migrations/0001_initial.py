
from south.db import db
from django.db import models
from mailer.models import *

class Migration:

    def forwards(self, orm):

        # Adding model 'Message'
        db.create_table('mailer_message', (
            ('id', orm['mailer.Message:id']),
            ('to_address', orm['mailer.Message:to_address']),
            ('from_address', orm['mailer.Message:from_address']),
            ('subject', orm['mailer.Message:subject']),
            ('message_body', orm['mailer.Message:message_body']),
            ('when_added', orm['mailer.Message:when_added']),
            ('priority', orm['mailer.Message:priority']),
        ))
        db.send_create_signal('mailer', ['Message'])

        # Adding model 'MessageLog'
        db.create_table('mailer_messagelog', (
            ('id', orm['mailer.MessageLog:id']),
            ('to_address', orm['mailer.MessageLog:to_address']),
            ('from_address', orm['mailer.MessageLog:from_address']),
            ('subject', orm['mailer.MessageLog:subject']),
            ('message_body', orm['mailer.MessageLog:message_body']),
            ('when_added', orm['mailer.MessageLog:when_added']),
            ('priority', orm['mailer.MessageLog:priority']),
            ('when_attempted', orm['mailer.MessageLog:when_attempted']),
            ('result', orm['mailer.MessageLog:result']),
            ('log_message', orm['mailer.MessageLog:log_message']),
        ))
        db.send_create_signal('mailer', ['MessageLog'])

        # Adding model 'DontSendEntry'
        db.create_table('mailer_dontsendentry', (
            ('id', orm['mailer.DontSendEntry:id']),
            ('to_address', orm['mailer.DontSendEntry:to_address']),
            ('when_added', orm['mailer.DontSendEntry:when_added']),
        ))
        db.send_create_signal('mailer', ['DontSendEntry'])



    def backwards(self, orm):

        # Deleting model 'Message'
        db.delete_table('mailer_message')

        # Deleting model 'MessageLog'
        db.delete_table('mailer_messagelog')

        # Deleting model 'DontSendEntry'
        db.delete_table('mailer_dontsendentry')



    models = {
        'mailer.dontsendentry': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_address': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'when_added': ('django.db.models.fields.DateTimeField', [], {})
        },
        'mailer.message': {
            'from_address': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_body': ('django.db.models.fields.TextField', [], {}),
            'priority': ('django.db.models.fields.CharField', [], {'default': "'2'", 'max_length': '1'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'to_address': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'when_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'mailer.messagelog': {
            'from_address': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log_message': ('django.db.models.fields.TextField', [], {}),
            'message_body': ('django.db.models.fields.TextField', [], {}),
            'priority': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'to_address': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'when_added': ('django.db.models.fields.DateTimeField', [], {}),
            'when_attempted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        }
    }

    complete_apps = ['mailer']
