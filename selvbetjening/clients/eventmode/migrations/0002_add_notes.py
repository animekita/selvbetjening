
from south.db import db
from django.db import models
from selvbetjening.clients.eventmode.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Note'
        db.create_table('eventmode_note', (
            ('note', models.TextField()),
            ('event', models.ForeignKey(orm['events.Event'])),
            ('id', models.AutoField(primary_key=True)),
            ('title', models.CharField(max_length=255)),
        ))
        db.send_create_signal('eventmode', ['Note'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Note'
        db.delete_table('eventmode_note')
        
    
    
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
        },
        'eventmode.note': {
            'event': ('models.ForeignKey', ['Event'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'note': ('models.TextField', [], {}),
            'title': ('models.CharField', [], {'max_length': '255'})
        }
    }
    
    complete_apps = ['eventmode']
