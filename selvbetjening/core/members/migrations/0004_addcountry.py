# coding=UTF-8

from south.db import db
from django.db import models
from selvbetjening.core.members.models import *

class Migration:

    def forwards(self, orm):

        # Adding field 'UserProfile.country'
        db.add_column('members_userprofile', 'country', orm['members.userprofile:country'])

        # Changing field 'UserProfile.city'
        # (to signature: django.db.models.fields.CharField(max_length=255, blank=True))
        db.alter_column('members_userprofile', 'city', orm['members.userprofile:city'])

        # Changing field 'UserProfile.street'
        # (to signature: django.db.models.fields.CharField(max_length=255, blank=True))
        db.alter_column('members_userprofile', 'street', orm['members.userprofile:street'])

        # Changing field 'UserProfile.dateofbirth'
        # (to signature: django.db.models.fields.DateField(null=True, blank=True))
        db.alter_column('members_userprofile', 'dateofbirth', orm['members.userprofile:dateofbirth'])

        # Changing field 'UserProfile.phonenumber'
        # (to signature: django.db.models.fields.PositiveIntegerField(null=True, blank=True))
        db.alter_column('members_userprofile', 'phonenumber', orm['members.userprofile:phonenumber'])

        # Changing field 'UserProfile.user'
        # (to signature: django.db.models.fields.related.ForeignKey(to=orm['auth.User'], unique=True, primary_key=True, db_column='user_id'))
        db.alter_column('members_userprofile', 'user_id', orm['members.userprofile:user'])

        # Changing field 'UserProfile.postalcode'
        # (to signature: django.db.models.fields.PositiveIntegerField(null=True, blank=True))
        db.alter_column('members_userprofile', 'postalcode', orm['members.userprofile:postalcode'])

        # Changing field 'UserProfile.send_me_email'
        # (to signature: django.db.models.fields.BooleanField(blank=True))
        db.alter_column('members_userprofile', 'send_me_email', orm['members.userprofile:send_me_email'])



    def backwards(self, orm):

        # Deleting field 'UserProfile.country'
        db.delete_column('members_userprofile', 'country_id')

        # Changing field 'UserProfile.city'
        # (to signature: models.CharField(_(u'city'), max_length=255, blank=True))
        db.alter_column('members_userprofile', 'city', orm['members.userprofile:city'])

        # Changing field 'UserProfile.street'
        # (to signature: models.CharField(_(u'street'), max_length=255, blank=True))
        db.alter_column('members_userprofile', 'street', orm['members.userprofile:street'])

        # Changing field 'UserProfile.dateofbirth'
        # (to signature: models.DateField(_(u'date of birth'), null=True, blank=True))
        db.alter_column('members_userprofile', 'dateofbirth', orm['members.userprofile:dateofbirth'])

        # Changing field 'UserProfile.phonenumber'
        # (to signature: models.PositiveIntegerField(_(u'phonenumber'), null=True, blank=True))
        db.alter_column('members_userprofile', 'phonenumber', orm['members.userprofile:phonenumber'])

        # Changing field 'UserProfile.user'
        # (to signature: models.ForeignKey(orm['auth.User'], unique=True, primary_key=True, db_column='user_id'))
        db.alter_column('members_userprofile', 'user_id', orm['members.userprofile:user'])

        # Changing field 'UserProfile.postalcode'
        # (to signature: models.PositiveIntegerField(_(u'postal code'), null=True, blank=True))
        db.alter_column('members_userprofile', 'postalcode', orm['members.userprofile:postalcode'])

        # Changing field 'UserProfile.send_me_email'
        # (to signature: models.BooleanField(_(u'Send me emails')))
        db.alter_column('members_userprofile', 'send_me_email', orm['members.userprofile:send_me_email'])



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
        'countries.country': {
            'Meta': {'db_table': "'country'"},
            'iso': ('django.db.models.fields.CharField', [], {'max_length': '2', 'primary_key': 'True'}),
            'iso3': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'numcode': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'printable_name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'members.userprofile': {
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'default': "'DK'", 'to': "orm['countries.Country']"}),
            'dateofbirth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'phonenumber': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'postalcode': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'send_me_email': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'user_id'"})
        }
    }

    complete_apps = ['members']
