# coding=UTF-8

from south.db import db
from django.db import models
from selvbetjening.data.members.models import *

class Migration:
    
    def forwards(self, orm):
        db.alter_column('members_userprofile', 'dateofbirth', models.DateField(_(u'date of birth'), null=True, blank=True))

    def backwards(self, orm):
        "Write your backwards migration here"
        pass
    
    models = {
        'members.userprofile': {
            'city': ('models.CharField', ["_(u'city')"], {'max_length': '255', 'blank': 'True'}),
            'dateofbirth': ('models.DateField', ["_(u'date of birth')"], {'null': 'True', 'blank': 'True'}),
            'phonenumber': ('models.PositiveIntegerField', ["_(u'phonenumber')"], {'null': 'True', 'blank': 'True'}),
            'postalcode': ('models.PositiveIntegerField', ["_(u'postal code')"], {'null': 'True', 'blank': 'True'}),
            'send_me_email': ('models.BooleanField', ["_(u'Send me emails')"], {}),
            'street': ('models.CharField', ["_(u'street')"], {'max_length': '255', 'blank': 'True'}),
            'user': ('models.ForeignKey', ['User'], {'unique': 'True', 'verbose_name': "_(u'user')", 'primary_key': 'True', 'db_column': "'user_id'"})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['members']
