# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EmailSpecification'
        db.create_table(u'mailcenter_emailspecification', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.CharField')(default='', max_length=64, blank=True)),
            ('source_enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('date_created', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('send_to_user', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('other_recipients', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'mailcenter', ['EmailSpecification'])

        # Adding M2M table for field recipients on 'EmailSpecification'
        m2m_table_name = db.shorten_name(u'mailcenter_emailspecification_recipients')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('emailspecification', models.ForeignKey(orm[u'mailcenter.emailspecification'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['emailspecification_id', 'user_id'])

        # Adding model 'UserConditions'
        db.create_table(u'mailcenter_userconditions', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('specification', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['mailcenter.EmailSpecification'], unique=True)),
            ('user_age_comparator', self.gf('django.db.models.fields.CharField')(max_length='1', blank=True)),
            ('user_age_argument', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal(u'mailcenter', ['UserConditions'])

        # Adding model 'AttendConditions'
        db.create_table(u'mailcenter_attendconditions', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('specification', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['mailcenter.EmailSpecification'], unique=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['events.Event'], null=True, blank=True)),
            ('attends_selection_comparator', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
            ('attends_state', self.gf('selvbetjening.core.models.ListField')(default='waiting', null=True, blank=True)),
        ))
        db.send_create_signal(u'mailcenter', ['AttendConditions'])

        # Adding M2M table for field attends_selection_argument on 'AttendConditions'
        m2m_table_name = db.shorten_name(u'mailcenter_attendconditions_attends_selection_argument')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('attendconditions', models.ForeignKey(orm[u'mailcenter.attendconditions'], null=False)),
            ('option', models.ForeignKey(orm['events.option'], null=False))
        ))
        db.create_unique(m2m_table_name, ['attendconditions_id', 'option_id'])

        # Adding model 'BoundAttendConditions'
        db.create_table(u'mailcenter_boundattendconditions', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('specification', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['mailcenter.EmailSpecification'], unique=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['events.Event'], null=True, blank=True)),
            ('attends_selection_comparator', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
            ('attends_state', self.gf('selvbetjening.core.models.ListField')(default='waiting', null=True, blank=True)),
        ))
        db.send_create_signal(u'mailcenter', ['BoundAttendConditions'])

        # Adding M2M table for field attends_selection_argument on 'BoundAttendConditions'
        m2m_table_name = db.shorten_name(u'mailcenter_boundattendconditions_attends_selection_argument')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('boundattendconditions', models.ForeignKey(orm[u'mailcenter.boundattendconditions'], null=False)),
            ('option', models.ForeignKey(orm['events.option'], null=False))
        ))
        db.create_unique(m2m_table_name, ['boundattendconditions_id', 'option_id'])


    def backwards(self, orm):
        # Deleting model 'EmailSpecification'
        db.delete_table(u'mailcenter_emailspecification')

        # Removing M2M table for field recipients on 'EmailSpecification'
        db.delete_table(db.shorten_name(u'mailcenter_emailspecification_recipients'))

        # Deleting model 'UserConditions'
        db.delete_table(u'mailcenter_userconditions')

        # Deleting model 'AttendConditions'
        db.delete_table(u'mailcenter_attendconditions')

        # Removing M2M table for field attends_selection_argument on 'AttendConditions'
        db.delete_table(db.shorten_name(u'mailcenter_attendconditions_attends_selection_argument'))

        # Deleting model 'BoundAttendConditions'
        db.delete_table(u'mailcenter_boundattendconditions')

        # Removing M2M table for field attends_selection_argument on 'BoundAttendConditions'
        db.delete_table(db.shorten_name(u'mailcenter_boundattendconditions_attends_selection_argument'))


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
        'events.event': {
            'Meta': {'object_name': 'Event'},
            'custom_change_message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'custom_signup_message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'custom_status_page': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enddate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Group']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum_attendees': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'move_to_accepted_policy': ('django.db.models.fields.CharField', [], {'default': "'always'", 'max_length': '32'}),
            'registration_open': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_custom_change_message': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_custom_signup_message': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_custom_status_page': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'startdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'events.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'events.option': {
            'Meta': {'ordering': "('order',)", 'object_name': 'Option'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.OptionGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_scope_edit_manage_accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'in_scope_edit_manage_attended': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'in_scope_edit_manage_waiting': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'in_scope_edit_registration': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'in_scope_view_manage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'in_scope_view_registration': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'in_scope_view_system_invoice': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'in_scope_view_user_invoice': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'selected_by_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'boolean'", 'max_length': '32'})
        },
        'events.optiongroup': {
            'Meta': {'ordering': "('-is_special', 'order')", 'object_name': 'OptionGroup'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Event']"}),
            'gatekeeper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Option']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_special': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'maximum_selected': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'minimum_selected': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'package_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'})
        },
        u'mailcenter.attendconditions': {
            'Meta': {'object_name': 'AttendConditions'},
            'attends_selection_argument': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['events.Option']", 'symmetrical': 'False', 'blank': 'True'}),
            'attends_selection_comparator': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'attends_state': ('selvbetjening.core.models.ListField', [], {'default': "'waiting'", 'null': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['events.Event']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'specification': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['mailcenter.EmailSpecification']", 'unique': 'True'})
        },
        u'mailcenter.boundattendconditions': {
            'Meta': {'object_name': 'BoundAttendConditions'},
            'attends_selection_argument': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['events.Option']", 'symmetrical': 'False', 'blank': 'True'}),
            'attends_selection_comparator': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'attends_state': ('selvbetjening.core.models.ListField', [], {'default': "'waiting'", 'null': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['events.Event']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'specification': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['mailcenter.EmailSpecification']", 'unique': 'True'})
        },
        u'mailcenter.emailspecification': {
            'Meta': {'object_name': 'EmailSpecification'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'date_created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'other_recipients': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'recipients': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False'}),
            'send_to_user': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'source_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'mailcenter.userconditions': {
            'Meta': {'object_name': 'UserConditions'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'specification': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['mailcenter.EmailSpecification']", 'unique': 'True'}),
            'user_age_argument': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'user_age_comparator': ('django.db.models.fields.CharField', [], {'max_length': "'1'", 'blank': 'True'})
        }
    }

    complete_apps = ['mailcenter']