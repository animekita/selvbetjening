# coding=UTF-8

from south.db import db
from django.db import models
from selvbetjening.core.members.models import *

class Migration:

    def forwards(self, orm):

        # Adding model 'UserProfile'
        db.create_table('members_userprofile', (
            ('city', models.CharField(_(u'city'), max_length=255, blank=True)),
            ('dateofbirth', models.DateField(_(u'date of birth'), null=True, blank=True)),
            ('street', models.CharField(_(u'street'), max_length=255, blank=True)),
            ('phonenumber', models.PositiveIntegerField(_(u'phonenumber'), null=True, blank=True)),
            ('user', models.ForeignKey(orm['auth.User'], unique=True, verbose_name=_(u'user'))),
            ('postalcode', models.PositiveIntegerField(_(u'postal code'), null=True, blank=True)),
            ('send_me_email', models.BooleanField(_(u'Send me emails'))),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('members', ['UserProfile'])



    def backwards(self, orm):

        # Deleting model 'UserProfile'
        db.delete_table('members_userprofile')



    models = {
        'members.userprofile': {
            'city': ('models.CharField', ["_(u'city')"], {'max_length': '255', 'blank': 'True'}),
            'dateofbirth': ('models.DateField', ["_(u'date of birth')"], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'phonenumber': ('models.PositiveIntegerField', ["_(u'phonenumber')"], {'null': 'True', 'blank': 'True'}),
            'postalcode': ('models.PositiveIntegerField', ["_(u'postal code')"], {'null': 'True', 'blank': 'True'}),
            'send_me_email': ('models.BooleanField', ["_(u'Send me emails')"], {}),
            'street': ('models.CharField', ["_(u'street')"], {'max_length': '255', 'blank': 'True'}),
            'user': ('models.ForeignKey', ['User'], {'unique': 'True', 'verbose_name': "_(u'user')"})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['members']
