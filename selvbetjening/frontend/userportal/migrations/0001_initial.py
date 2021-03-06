# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserPrivacy'
        db.create_table(u'profile_userprivacy', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('public_profile', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('public_name', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('public_age', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('public_sex', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('public_email', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('public_phonenumber', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('public_town', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('public_contact', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('public_websites', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('public_join_date', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'userportal', ['UserPrivacy'])


    def backwards(self, orm):
        # Deleting model 'UserPrivacy'
        db.delete_table(u'profile_userprivacy')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'userportal.userprivacy': {
            'Meta': {'object_name': 'UserPrivacy'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'public_age': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'public_contact': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'public_email': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'public_join_date': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'public_name': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'public_phonenumber': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'public_profile': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'public_sex': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'public_town': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'public_websites': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['userportal']