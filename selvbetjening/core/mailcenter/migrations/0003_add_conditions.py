# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'AttendConditions'
        db.create_table('mailcenter_attendconditions', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('specification', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['mailcenter.EmailSpecification'], unique=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['events.Event'], null=True, blank=True)),
            ('attends_selection_comparator', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
            ('attends_state', self.gf('selvbetjening.core.models.ListField')(default='waiting', null=True, blank=True)),
        ))
        db.send_create_signal('mailcenter', ['AttendConditions'])

        # Adding M2M table for field attends_selection_argument on 'AttendConditions'
        db.create_table('mailcenter_attendconditions_attends_selection_argument', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('attendconditions', models.ForeignKey(orm['mailcenter.attendconditions'], null=False)),
            ('option', models.ForeignKey(orm['events.option'], null=False))
        ))
        db.create_unique('mailcenter_attendconditions_attends_selection_argument', ['attendconditions_id', 'option_id'])

        # Adding model 'UserConditions'
        db.create_table('mailcenter_userconditions', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('specification', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['mailcenter.EmailSpecification'], unique=True)),
            ('user_age_comparator', self.gf('django.db.models.fields.CharField')(max_length='1', blank=True)),
            ('user_age_argument', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal('mailcenter', ['UserConditions'])

        # Adding model 'BoundAttendConditions'
        db.create_table('mailcenter_boundattendconditions', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('specification', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['mailcenter.EmailSpecification'], unique=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['events.Event'], null=True, blank=True)),
            ('attends_selection_comparator', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
            ('attends_state', self.gf('selvbetjening.core.models.ListField')(default='waiting', null=True, blank=True)),
        ))
        db.send_create_signal('mailcenter', ['BoundAttendConditions'])

        # Adding M2M table for field attends_selection_argument on 'BoundAttendConditions'
        db.create_table('mailcenter_boundattendconditions_attends_selection_argument', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('boundattendconditions', models.ForeignKey(orm['mailcenter.boundattendconditions'], null=False)),
            ('option', models.ForeignKey(orm['events.option'], null=False))
        ))
        db.create_unique('mailcenter_boundattendconditions_attends_selection_argument', ['boundattendconditions_id', 'option_id'])

        # Adding field 'EmailSpecification.event'
        db.add_column('mailcenter_emailspecification', 'event', self.gf('django.db.models.fields.CharField')(default='', max_length=64, blank=True), keep_default=False)

        # Adding field 'EmailSpecification.source_enabled'
        db.add_column('mailcenter_emailspecification', 'source_enabled', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding M2M table for field recipients on 'EmailSpecification'
        db.create_table('mailcenter_emailspecification_recipients', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('emailspecification', models.ForeignKey(orm['mailcenter.emailspecification'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('mailcenter_emailspecification_recipients', ['emailspecification_id', 'user_id'])


    def backwards(self, orm):
        
        # Deleting model 'AttendConditions'
        db.delete_table('mailcenter_attendconditions')

        # Removing M2M table for field attends_selection_argument on 'AttendConditions'
        db.delete_table('mailcenter_attendconditions_attends_selection_argument')

        # Deleting model 'UserConditions'
        db.delete_table('mailcenter_userconditions')

        # Deleting model 'BoundAttendConditions'
        db.delete_table('mailcenter_boundattendconditions')

        # Removing M2M table for field attends_selection_argument on 'BoundAttendConditions'
        db.delete_table('mailcenter_boundattendconditions_attends_selection_argument')

        # Deleting field 'EmailSpecification.event'
        db.delete_column('mailcenter_emailspecification', 'event')

        # Deleting field 'EmailSpecification.source_enabled'
        db.delete_column('mailcenter_emailspecification', 'source_enabled')

        # Removing M2M table for field recipients on 'EmailSpecification'
        db.delete_table('mailcenter_emailspecification_recipients')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum_attendees': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'move_to_accepted_policy': ('django.db.models.fields.CharField', [], {'default': "'always'", 'max_length': '32'}),
            'registration_open': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_custom_change_message': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_custom_signup_message': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_custom_status_page': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'startdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'events.option': {
            'Meta': {'object_name': 'Option'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'freeze_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.OptionGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum_attendees': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'})
        },
        'events.optiongroup': {
            'Meta': {'object_name': 'OptionGroup'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Event']"}),
            'freeze_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum_attendees': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'maximum_selected': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'minimum_selected': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'public_statistic': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'mailcenter.attendconditions': {
            'Meta': {'object_name': 'AttendConditions'},
            'attends_selection_argument': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['events.Option']", 'symmetrical': 'False', 'blank': 'True'}),
            'attends_selection_comparator': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'attends_state': ('selvbetjening.core.models.ListField', [], {'default': "'waiting'", 'null': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['events.Event']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'specification': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['mailcenter.EmailSpecification']", 'unique': 'True'})
        },
        'mailcenter.boundattendconditions': {
            'Meta': {'object_name': 'BoundAttendConditions'},
            'attends_selection_argument': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['events.Option']", 'symmetrical': 'False', 'blank': 'True'}),
            'attends_selection_comparator': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'attends_state': ('selvbetjening.core.models.ListField', [], {'default': "'waiting'", 'null': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['events.Event']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'specification': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['mailcenter.EmailSpecification']", 'unique': 'True'})
        },
        'mailcenter.emailspecification': {
            'Meta': {'object_name': 'EmailSpecification'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'date_created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipients': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'source_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'mailcenter.userconditions': {
            'Meta': {'object_name': 'UserConditions'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'specification': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['mailcenter.EmailSpecification']", 'unique': 'True'}),
            'user_age_argument': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'user_age_comparator': ('django.db.models.fields.CharField', [], {'max_length': "'1'", 'blank': 'True'})
        }
    }

    complete_apps = ['mailcenter']
