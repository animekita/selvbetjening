# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
import pprint


class Migration(DataMigration):

    def does_line_match_selections(self, line, selections):

        index = -1

        for i in xrange(0, len(selections)):
            if selections[i].option.name in line.description:
                index = i
                break

        if index == -1:
            return False
        else:
            del selections[index]
            return True

    def match_with_existing_options(self, line, options, attendee, orm):

        for option in options:

            if option.name in line.description and option.price == line.price:

                instance, created = orm['events.Selection'].objects.get_or_create(
                    attendee=attendee,
                    option=option
                )

                assert created

                return True

        return False

    def forwards(self, orm):

        for event in orm['events.Event'].objects.all():

            try:
                option_group = orm['events.OptionGroup'].objects.get(event=event, is_special=True)
            except orm['events.OptionGroup'].DoesNotExist:
                option_group = orm['events.OptionGroup'].objects.create(event=event, is_special=True, order=-100)

            # For all legacy systems (pre Selvbetjening 8) we want to preserve any data available in the
            # invoices not present in the selections

            new_options = []

            for attendee in orm['events.Attend'].objects.filter(event=event).select_related():

                selections = list(attendee.selection_set.all())

                for line in attendee.invoice.line_set.all():

                    # for each line we
                    # 1. match with a selection

                    if self.does_line_match_selections(line, selections):
                        # match, just continue
                        pass

                    # 2. match with an existing option

                    elif self.match_with_existing_options(line, new_options, attendee, orm):
                        # match, just continue
                        pass

                    # 3. create a new option

                    else:

                        description = line.description

                        # we also have cases where we prefix with the event name
                        if event.title in description and ':' in description:
                            description = description.split(':')[1].strip()

                        option = orm['events.Option'].objects.create(
                            group=option_group,
                            name=description,
                            price=line.price,

                            in_scope_view_registration=False,
                            in_scope_view_manage=False,
                            in_scope_view_user_invoice=True,
                            in_scope_view_system_invoice=True,

                            in_scope_edit_registration=False,
                            in_scope_edit_manage_waiting=False,
                            in_scope_edit_manage_accepted=False,
                            in_scope_edit_manage_attended=False
                        )

                        new_options.append(option)

                        orm['events.Selection'].objects.create(
                            option=option,
                            attendee=attendee
                        )

                # check that all selections have been identified using lines, if not we have an error and should stop

                assert len(selections) == 0


    def backwards(self, orm):
        "Write your backwards methods here."

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
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['invoice.Invoice']", 'blank': 'True'}),
            'is_new': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'Meta': {'ordering': "('order',)", 'object_name': 'OptionGroup'},
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
        u'invoice.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'paid': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'total_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'invoice.invoiceline': {
            'Meta': {'object_name': 'InvoiceLine'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'group_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'line_set'", 'to': u"orm['invoice.Invoice']"}),
            'managed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'})
        },
        u'invoice.invoicerevision': {
            'Meta': {'object_name': 'InvoiceRevision'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'revision_set'", 'to': u"orm['invoice.Invoice']"}),
            'total_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'})
        },
        u'invoice.line': {
            'Meta': {'object_name': 'Line'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'group_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'managed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'revision': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'line_set'", 'to': u"orm['invoice.InvoiceRevision']"})
        },
        u'invoice.payment': {
            'Meta': {'object_name': 'Payment'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['invoice.Invoice']"}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'signee': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'signed_payment_set'", 'null': 'True', 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['invoice', 'events']
    symmetrical = True
