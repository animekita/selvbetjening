# coding=UTF-8

from south.db import db
from django.db import models
from selvbetjening.data.events.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'Attend.state'
        db.add_column('events_attend', 'state', orm['events.attend:state'])
        
        # Adding field 'Event.move_to_accepted_policy'
        db.add_column('events_event', 'move_to_accepted_policy', orm['events.event:move_to_accepted_policy'])
        
        # Changing field 'Event.startdate'
        # (to signature: django.db.models.fields.DateField(null=True, blank=True))
        db.alter_column('events_event', 'startdate', orm['events.event:startdate'])
        
        # Changing field 'Event.enddate'
        # (to signature: django.db.models.fields.DateField(null=True, blank=True))
        db.alter_column('events_event', 'enddate', orm['events.event:enddate'])
        
        # Changing field 'Event.title'
        # (to signature: django.db.models.fields.CharField(max_length=255))
        db.alter_column('events_event', 'title', orm['events.event:title'])
        
        # Changing field 'Event.show_change_confirmation'
        # (to signature: django.db.models.fields.BooleanField(blank=True))
        db.alter_column('events_event', 'show_change_confirmation', orm['events.event:show_change_confirmation'])
        
        # Changing field 'Event.registration_open'
        # (to signature: django.db.models.fields.BooleanField(blank=True))
        db.alter_column('events_event', 'registration_open', orm['events.event:registration_open'])
        
        # Changing field 'Event.show_registration_confirmation'
        # (to signature: django.db.models.fields.BooleanField(blank=True))
        db.alter_column('events_event', 'show_registration_confirmation', orm['events.event:show_registration_confirmation'])
        
        # Changing field 'Event.maximum_attendees'
        # (to signature: django.db.models.fields.IntegerField())
        db.alter_column('events_event', 'maximum_attendees', orm['events.event:maximum_attendees'])
        
        # Changing field 'Event.show_invoice_page'
        # (to signature: django.db.models.fields.BooleanField(blank=True))
        db.alter_column('events_event', 'show_invoice_page', orm['events.event:show_invoice_page'])
        
        # Changing field 'Attend.has_attended'
        # (to signature: django.db.models.fields.BooleanField(blank=True))
        db.alter_column('events_attend', 'has_attended', orm['events.attend:has_attended'])
        
        # Changing field 'OptionGroup.freeze_time'
        # (to signature: django.db.models.fields.DateTimeField(null=True, blank=True))
        db.alter_column('events_optiongroup', 'freeze_time', orm['events.optiongroup:freeze_time'])
        
        # Changing field 'OptionGroup.minimum_selected'
        # (to signature: django.db.models.fields.IntegerField())
        db.alter_column('events_optiongroup', 'minimum_selected', orm['events.optiongroup:minimum_selected'])
        
        # Changing field 'OptionGroup.maximum_selected'
        # (to signature: django.db.models.fields.IntegerField())
        db.alter_column('events_optiongroup', 'maximum_selected', orm['events.optiongroup:maximum_selected'])
        
        # Changing field 'OptionGroup.maximum_attendees'
        # (to signature: django.db.models.fields.IntegerField())
        db.alter_column('events_optiongroup', 'maximum_attendees', orm['events.optiongroup:maximum_attendees'])
        
        # Changing field 'OptionGroup.order'
        # (to signature: django.db.models.fields.IntegerField())
        db.alter_column('events_optiongroup', 'order', orm['events.optiongroup:order'])
        
        # Changing field 'OptionGroup.name'
        # (to signature: django.db.models.fields.CharField(max_length=255))
        db.alter_column('events_optiongroup', 'name', orm['events.optiongroup:name'])
        
        # Changing field 'Option.maximum_attendees'
        # (to signature: django.db.models.fields.IntegerField(null=True, blank=True))
        db.alter_column('events_option', 'maximum_attendees', orm['events.option:maximum_attendees'])
        
        # Changing field 'Option.freeze_time'
        # (to signature: django.db.models.fields.DateTimeField(null=True, blank=True))
        db.alter_column('events_option', 'freeze_time', orm['events.option:freeze_time'])
        
        # Changing field 'Option.order'
        # (to signature: django.db.models.fields.IntegerField())
        db.alter_column('events_option', 'order', orm['events.option:order'])
        
        # Changing field 'Option.name'
        # (to signature: django.db.models.fields.CharField(max_length=255))
        db.alter_column('events_option', 'name', orm['events.option:name'])
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'Attend.state'
        db.delete_column('events_attend', 'state')
        
        # Deleting field 'Event.move_to_accepted_policy'
        db.delete_column('events_event', 'move_to_accepted_policy')
        
        # Changing field 'Event.startdate'
        # (to signature: models.DateField(_(u'start date'), null=True, blank=True))
        db.alter_column('events_event', 'startdate', orm['events.event:startdate'])
        
        # Changing field 'Event.enddate'
        # (to signature: models.DateField(_(u'end date'), null=True, blank=True))
        db.alter_column('events_event', 'enddate', orm['events.event:enddate'])
        
        # Changing field 'Event.title'
        # (to signature: models.CharField(_(u'title'), max_length=255))
        db.alter_column('events_event', 'title', orm['events.event:title'])
        
        # Changing field 'Event.show_change_confirmation'
        # (to signature: models.BooleanField())
        db.alter_column('events_event', 'show_change_confirmation', orm['events.event:show_change_confirmation'])
        
        # Changing field 'Event.registration_open'
        # (to signature: models.BooleanField(_(u'registration open')))
        db.alter_column('events_event', 'registration_open', orm['events.event:registration_open'])
        
        # Changing field 'Event.show_registration_confirmation'
        # (to signature: models.BooleanField())
        db.alter_column('events_event', 'show_registration_confirmation', orm['events.event:show_registration_confirmation'])
        
        # Changing field 'Event.maximum_attendees'
        # (to signature: models.IntegerField(_('Maximum attendees')))
        db.alter_column('events_event', 'maximum_attendees', orm['events.event:maximum_attendees'])
        
        # Changing field 'Event.show_invoice_page'
        # (to signature: models.BooleanField())
        db.alter_column('events_event', 'show_invoice_page', orm['events.event:show_invoice_page'])
        
        # Changing field 'Attend.has_attended'
        # (to signature: models.BooleanField())
        db.alter_column('events_attend', 'has_attended', orm['events.attend:has_attended'])
        
        # Changing field 'OptionGroup.freeze_time'
        # (to signature: models.DateTimeField(_('Freeze time'), null=True, blank=True))
        db.alter_column('events_optiongroup', 'freeze_time', orm['events.optiongroup:freeze_time'])
        
        # Changing field 'OptionGroup.minimum_selected'
        # (to signature: models.IntegerField(_('Minimum selected')))
        db.alter_column('events_optiongroup', 'minimum_selected', orm['events.optiongroup:minimum_selected'])
        
        # Changing field 'OptionGroup.maximum_selected'
        # (to signature: models.IntegerField(_('Maximum selected')))
        db.alter_column('events_optiongroup', 'maximum_selected', orm['events.optiongroup:maximum_selected'])
        
        # Changing field 'OptionGroup.maximum_attendees'
        # (to signature: models.IntegerField(_('Maximum attendees')))
        db.alter_column('events_optiongroup', 'maximum_attendees', orm['events.optiongroup:maximum_attendees'])
        
        # Changing field 'OptionGroup.order'
        # (to signature: models.IntegerField(_('Order')))
        db.alter_column('events_optiongroup', 'order', orm['events.optiongroup:order'])
        
        # Changing field 'OptionGroup.name'
        # (to signature: models.CharField(_('Name'), max_length=255))
        db.alter_column('events_optiongroup', 'name', orm['events.optiongroup:name'])
        
        # Changing field 'Option.maximum_attendees'
        # (to signature: models.IntegerField(_('Maximum attendees'), null=True, blank=True))
        db.alter_column('events_option', 'maximum_attendees', orm['events.option:maximum_attendees'])
        
        # Changing field 'Option.freeze_time'
        # (to signature: models.DateTimeField(_('Freeze time'), null=True, blank=True))
        db.alter_column('events_option', 'freeze_time', orm['events.option:freeze_time'])
        
        # Changing field 'Option.order'
        # (to signature: models.IntegerField(_('Order')))
        db.alter_column('events_option', 'order', orm['events.option:order'])
        
        # Changing field 'Option.name'
        # (to signature: models.CharField(_('Name'), max_length=255))
        db.alter_column('events_option', 'name', orm['events.option:name'])
        
    
    
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
        'events.attend': {
            'Meta': {'unique_together': "(('event', 'user'),)"},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Event']"}),
            'has_attended': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['invoice.Invoice']", 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'waiting'", 'max_length': '32'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'events.event': {
            'change_confirmation': ('HTMLField', [], {'blank': 'True'}),
            'description': ('HTMLField', ["_(u'description')"], {'blank': 'True'}),
            'enddate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_page': ('HTMLField', [], {'blank': 'True'}),
            'maximum_attendees': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'move_to_accepted_policy': ('django.db.models.fields.CharField', [], {'default': "'always'", 'max_length': '32'}),
            'registration_confirmation': ('HTMLField', [], {'blank': 'True'}),
            'registration_open': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'show_change_confirmation': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'show_invoice_page': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'show_registration_confirmation': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'startdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'events.option': {
            'description': ('HTMLField', ["_('Description')"], {'blank': 'True'}),
            'freeze_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.OptionGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum_attendees': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'})
        },
        'events.optiongroup': {
            'description': ('HTMLField', ["_('Description')"], {'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Event']"}),
            'freeze_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum_attendees': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'maximum_selected': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'minimum_selected': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'events.selection': {
            'Meta': {'unique_together': "(('attendee', 'option'),)"},
            'attendee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Attend']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Option']"}),
            'suboption': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.SubOption']", 'null': 'True', 'blank': 'True'})
        },
        'events.suboption': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Option']"})
        },
        'invoice.invoice': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }
    
    complete_apps = ['events']
