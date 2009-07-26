
from south.db import db
from django.db import models
from selvbetjening.clients.eventmode.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'EventmodeMachine'
        db.create_table('eventmode_eventmodemachine', (
            ('active', models.BooleanField(default=False)),
            ('passphrase', models.CharField(max_length=255)),
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(max_length=255)),
            ('event', models.ForeignKey(orm['events.Event'])),
        ))
        db.send_create_signal('eventmode', ['EventmodeMachine'])
        
        # Creating unique_together for [event, passphrase] on EventmodeMachine.
        db.create_unique('eventmode_eventmodemachine', ['event_id', 'passphrase'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'EventmodeMachine'
        db.delete_table('eventmode_eventmodemachine')
        
        # Deleting unique_together for [event, passphrase] on EventmodeMachine.
        db.delete_unique('eventmode_eventmodemachine', ['event_id', 'passphrase'])
        
    
    
    models = {
        'events.event': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'eventmode.eventmodemachine': {
            'Meta': {'unique_together': "('event','passphrase')"},
            'active': ('models.BooleanField', [], {'default': 'False'}),
            'event': ('models.ForeignKey', ['Event'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '255'}),
            'passphrase': ('models.CharField', [], {'max_length': '255'})
        }
    }
    
    complete_apps = ['eventmode']
