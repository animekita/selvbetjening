# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Group'
        db.create_table(u'events_group', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('events', ['Group'])

        # Adding model 'Event'
        db.create_table(u'events_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Group'], null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('startdate', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('enddate', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('move_to_accepted_policy', self.gf('django.db.models.fields.CharField')(default='always', max_length=32)),
            ('maximum_attendees', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('registration_open', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_custom_signup_message', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('custom_signup_message', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('show_custom_change_message', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('custom_change_message', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('show_custom_status_page', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('custom_status_page', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('events', ['Event'])

        # Adding model 'Attend'
        db.create_table(u'events_attend', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Event'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('state', self.gf('django.db.models.fields.CharField')(default='waiting', max_length=32)),
            ('is_new', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('change_timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('registration_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('changed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=6, decimal_places=2)),
            ('paid', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=6, decimal_places=2)),
        ))
        db.send_create_signal('events', ['Attend'])

        # Adding unique constraint on 'Attend', fields ['event', 'user']
        db.create_unique(u'events_attend', ['event_id', 'user_id'])

        # Adding model 'AttendStateChange'
        db.create_table(u'events_attendstatechange', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('attendee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='state_history', to=orm['events.Attend'])),
        ))
        db.send_create_signal('events', ['AttendStateChange'])

        # Adding model 'AttendeeComment'
        db.create_table(u'events_attendeecomment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('attendee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comment_set', to=orm['events.Attend'])),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('comment', self.gf('django.db.models.fields.TextField')()),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('events', ['AttendeeComment'])

        # Adding model 'OptionGroup'
        db.create_table(u'events_optiongroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Event'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('minimum_selected', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('maximum_selected', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('gatekeeper', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Option'], null=True, blank=True)),
            ('package_price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=6, decimal_places=2)),
            ('is_special', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('events', ['OptionGroup'])

        # Adding model 'Option'
        db.create_table(u'events_option', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.OptionGroup'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('type', self.gf('django.db.models.fields.CharField')(default='boolean', max_length=32)),
            ('in_scope_view_registration', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('in_scope_view_manage', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('in_scope_view_user_invoice', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('in_scope_view_system_invoice', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('in_scope_edit_registration', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('in_scope_edit_manage_waiting', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('in_scope_edit_manage_accepted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('in_scope_edit_manage_attended', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('selected_by_default', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=6, decimal_places=2)),
        ))
        db.send_create_signal('events', ['Option'])

        # Adding model 'SubOption'
        db.create_table(u'events_suboption', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('option', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Option'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=None, null=True, max_digits=6, decimal_places=2, blank=True)),
        ))
        db.send_create_signal('events', ['SubOption'])

        # Adding model 'Selection'
        db.create_table(u'events_selection', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('attendee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Attend'])),
            ('option', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Option'])),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('suboption', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.SubOption'], null=True, blank=True)),
        ))
        db.send_create_signal('events', ['Selection'])

        # Adding unique constraint on 'Selection', fields ['attendee', 'option']
        db.create_unique(u'events_selection', ['attendee_id', 'option_id'])

        # Adding model 'Payment'
        db.create_table(u'events_payment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('attendee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Attend'], null=True, on_delete=models.SET_NULL)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
            ('signee', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='signee_payment_set', null=True, to=orm['auth.User'])),
            ('note', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('events', ['Payment'])


    def backwards(self, orm):
        # Removing unique constraint on 'Selection', fields ['attendee', 'option']
        db.delete_unique(u'events_selection', ['attendee_id', 'option_id'])

        # Removing unique constraint on 'Attend', fields ['event', 'user']
        db.delete_unique(u'events_attend', ['event_id', 'user_id'])

        # Deleting model 'Group'
        db.delete_table(u'events_group')

        # Deleting model 'Event'
        db.delete_table(u'events_event')

        # Deleting model 'Attend'
        db.delete_table(u'events_attend')

        # Deleting model 'AttendStateChange'
        db.delete_table(u'events_attendstatechange')

        # Deleting model 'AttendeeComment'
        db.delete_table(u'events_attendeecomment')

        # Deleting model 'OptionGroup'
        db.delete_table(u'events_optiongroup')

        # Deleting model 'Option'
        db.delete_table(u'events_option')

        # Deleting model 'SubOption'
        db.delete_table(u'events_suboption')

        # Deleting model 'Selection'
        db.delete_table(u'events_selection')

        # Deleting model 'Payment'
        db.delete_table(u'events_payment')


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
        'events.attend': {
            'Meta': {'unique_together': "(('event', 'user'),)", 'object_name': 'Attend'},
            'change_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_new': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'paid': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'registration_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'waiting'", 'max_length': '32'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        'events.attendeecomment': {
            'Meta': {'object_name': 'AttendeeComment'},
            'attendee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comment_set'", 'to': "orm['events.Attend']"}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'events.attendstatechange': {
            'Meta': {'object_name': 'AttendStateChange'},
            'attendee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'state_history'", 'to': "orm['events.Attend']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
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
        'events.payment': {
            'Meta': {'object_name': 'Payment'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'attendee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Attend']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'signee': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'signee_payment_set'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        'events.selection': {
            'Meta': {'unique_together': "(('attendee', 'option'),)", 'object_name': 'Selection'},
            'attendee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Attend']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Option']"}),
            'suboption': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.SubOption']", 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'events.suboption': {
            'Meta': {'object_name': 'SubOption'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Option']"}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': 'None', 'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'})
        }
    }

    complete_apps = ['events']