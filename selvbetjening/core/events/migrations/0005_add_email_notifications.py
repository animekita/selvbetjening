# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Event.notify_on_registration'
        db.add_column(u'events_event', 'notify_on_registration',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='notify_event_on_registration', null=True, to=orm['mailcenter.EmailSpecification']),
                      keep_default=False)

        # Adding field 'Event.notify_on_registration_update'
        db.add_column(u'events_event', 'notify_on_registration_update',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='notify_event_on_registration_update', null=True, to=orm['mailcenter.EmailSpecification']),
                      keep_default=False)

        # Adding field 'Event.notify_on_payment'
        db.add_column(u'events_event', 'notify_on_payment',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='notify_event_on_payment_registration', null=True, to=orm['mailcenter.EmailSpecification']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Event.notify_on_registration'
        db.delete_column(u'events_event', 'notify_on_registration_id')

        # Deleting field 'Event.notify_on_registration_update'
        db.delete_column(u'events_event', 'notify_on_registration_update_id')

        # Deleting field 'Event.notify_on_payment'
        db.delete_column(u'events_event', 'notify_on_payment_id')


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
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'location_link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'maximum_attendees': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'move_to_accepted_policy': ('django.db.models.fields.CharField', [], {'default': "'always'", 'max_length': '32'}),
            'notify_on_payment': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'notify_event_on_payment_registration'", 'null': 'True', 'to': u"orm['mailcenter.EmailSpecification']"}),
            'notify_on_registration': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'notify_event_on_registration'", 'null': 'True', 'to': u"orm['mailcenter.EmailSpecification']"}),
            'notify_on_registration_update': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'notify_event_on_registration_update'", 'null': 'True', 'to': u"orm['mailcenter.EmailSpecification']"}),
            'registration_open': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_custom_change_message': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_custom_signup_message': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_custom_status_page': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'startdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'tagline': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
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
            'in_scope_view_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
        },
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

    complete_apps = ['events']