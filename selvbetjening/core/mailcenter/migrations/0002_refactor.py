# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'AttendConditions'
        db.delete_table(u'mailcenter_attendconditions')

        # Removing M2M table for field attends_selection_argument on 'AttendConditions'
        db.delete_table(db.shorten_name(u'mailcenter_attendconditions_attends_selection_argument'))

        # Deleting model 'BoundAttendConditions'
        db.delete_table(u'mailcenter_boundattendconditions')

        # Removing M2M table for field attends_selection_argument on 'BoundAttendConditions'
        db.delete_table(db.shorten_name(u'mailcenter_boundattendconditions_attends_selection_argument'))

        # Deleting model 'UserConditions'
        db.delete_table(u'mailcenter_userconditions')

        # Deleting field 'EmailSpecification.other_recipients'
        db.delete_column(u'mailcenter_emailspecification', 'other_recipients')

        # Deleting field 'EmailSpecification.source_enabled'
        db.delete_column(u'mailcenter_emailspecification', 'source_enabled')

        # Deleting field 'EmailSpecification.send_to_user'
        db.delete_column(u'mailcenter_emailspecification', 'send_to_user')

        # Deleting field 'EmailSpecification.event'
        db.delete_column(u'mailcenter_emailspecification', 'event')

        # Adding field 'EmailSpecification.body_format'
        db.add_column(u'mailcenter_emailspecification', 'body_format',
                      self.gf('django.db.models.fields.CharField')(default='markdown', max_length=32),
                      keep_default=False)

        # Adding field 'EmailSpecification.template_context'
        db.add_column(u'mailcenter_emailspecification', 'template_context',
                      self.gf('django.db.models.fields.CharField')(default='user', max_length=32),
                      keep_default=False)

        # Removing M2M table for field recipients on 'EmailSpecification'
        db.delete_table(db.shorten_name(u'mailcenter_emailspecification_recipients'))


    def backwards(self, orm):
        # Adding model 'AttendConditions'
        db.create_table(u'mailcenter_attendconditions', (
            ('attends_state', self.gf('selvbetjening.core.models.ListField')(default='waiting', null=True, blank=True)),
            ('specification', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['mailcenter.EmailSpecification'], unique=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('attends_selection_comparator', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['events.Event'], null=True, blank=True)),
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
            ('attends_state', self.gf('selvbetjening.core.models.ListField')(default='waiting', null=True, blank=True)),
            ('specification', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['mailcenter.EmailSpecification'], unique=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('attends_selection_comparator', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['events.Event'], null=True, blank=True)),
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

        # Adding model 'UserConditions'
        db.create_table(u'mailcenter_userconditions', (
            ('specification', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['mailcenter.EmailSpecification'], unique=True)),
            ('user_age_argument', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_age_comparator', self.gf('django.db.models.fields.CharField')(max_length='1', blank=True)),
        ))
        db.send_create_signal(u'mailcenter', ['UserConditions'])

        # Adding field 'EmailSpecification.other_recipients'
        db.add_column(u'mailcenter_emailspecification', 'other_recipients',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'EmailSpecification.source_enabled'
        db.add_column(u'mailcenter_emailspecification', 'source_enabled',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'EmailSpecification.send_to_user'
        db.add_column(u'mailcenter_emailspecification', 'send_to_user',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'EmailSpecification.event'
        db.add_column(u'mailcenter_emailspecification', 'event',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=64, blank=True),
                      keep_default=False)

        # Deleting field 'EmailSpecification.body_format'
        db.delete_column(u'mailcenter_emailspecification', 'body_format')

        # Deleting field 'EmailSpecification.template_context'
        db.delete_column(u'mailcenter_emailspecification', 'template_context')

        # Adding M2M table for field recipients on 'EmailSpecification'
        m2m_table_name = db.shorten_name(u'mailcenter_emailspecification_recipients')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('emailspecification', models.ForeignKey(orm[u'mailcenter.emailspecification'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['emailspecification_id', 'user_id'])


    models = {
        u'mailcenter.emailspecification': {
            'Meta': {'object_name': 'EmailSpecification'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'body_format': ('django.db.models.fields.CharField', [], {'default': "'markdown'", 'max_length': '32'}),
            'date_created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'template_context': ('django.db.models.fields.CharField', [], {'default': "'user'", 'max_length': '32'})
        }
    }

    complete_apps = ['mailcenter']