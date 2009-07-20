# coding=UTF-8

from south.db import db
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from selvbetjening.data.events.models import *

class Migration:
    
    no_dry_run = True
    
    def forwards(self, orm):
        for user in orm['auth.User'].objects.all():
            for option in user.option_set.all():
                try:
                    attendee = orm.Attend.objects.get(user=user, event=option.group.event)
                    attendee.selection_set.create(option=option)
                except ObjectDoesNotExist:
                    pass
    
    def backwards(self, orm):
        "Write your backwards migration here"
    
    
    models = {
        'events.event': {
            'change_confirmation': ('HTMLField', [], {'blank': 'True'}),
            'description': ('HTMLField', ["_(u'description')"], {'blank': 'True'}),
            'enddate': ('models.DateField', ["_(u'end date')"], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'maximum_attendees': ('models.IntegerField', ["_('Maximum attendees')"], {'default': '0'}),
            'registration_confirmation': ('HTMLField', [], {'blank': 'True'}),
            'registration_open': ('models.BooleanField', ["_(u'registration open')"], {}),
            'show_change_confirmation': ('models.BooleanField', [], {'default': 'False'}),
            'show_registration_confirmation': ('models.BooleanField', [], {'default': 'False'}),
            'startdate': ('models.DateField', ["_(u'start date')"], {'null': 'True', 'blank': 'True'}),
            'title': ('models.CharField', ["_(u'title')"], {'max_length': '255'})
        },
        'events.suboption': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.TextField', [], {'max_length': '255'}),
            'option': ('models.ForeignKey', ['Option'], {})
        },
        'events.attend': {
            'Meta': {'unique_together': "('event','user')"},
            'event': ('models.ForeignKey', ['Event'], {}),
            'has_attended': ('models.BooleanField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('models.ForeignKey', ['Invoice'], {'blank': 'True'}),
            'user': ('models.ForeignKey', ['User'], {})
        },
        'auth.message': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'message': ('models.TextField', ["_('message')"], {}),
            'user': ('models.ForeignKey', ['User'], {})
        },
        'auth.user': {
            'date_joined': ('models.DateTimeField', ["_('date joined')"], {'default': 'None'}),
            'email': ('models.EmailField', ["_('e-mail address')"], {'blank': 'True'}),
            'first_name': ('models.CharField', ["_('first name')"], {'max_length': '30', 'blank': 'True'}),
            'groups': ('models.ManyToManyField', ['Group'], {'verbose_name': "_('groups')", 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('models.BooleanField', ["_('active')"], {'default': 'True'}),
            'is_staff': ('models.BooleanField', ["_('staff status')"], {'default': 'False'}),
            'is_superuser': ('models.BooleanField', ["_('superuser status')"], {'default': 'False'}),
            'last_login': ('models.DateTimeField', ["_('last login')"], {'default': 'None'}),
            'last_name': ('models.CharField', ["_('last name')"], {'max_length': '30', 'blank': 'True'}),
            'password': ('models.CharField', ["_('password')"], {'max_length': '128'}),
            'user_permissions': ('models.ManyToManyField', ['Permission'], {'verbose_name': "_('user permissions')", 'blank': 'True'}),
            'username': ('models.CharField', ["_('username')"], {'unique': 'True', 'max_length': '30'})
        },
        'invoice.invoice': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'events.selection': {
            'Meta': {'unique_together': "(('attendee','option'))"},
            'attendee': ('models.ForeignKey', ['Attend'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'option': ('models.ForeignKey', ['Option'], {}),
            'suboption': ('models.ForeignKey', ['SubOption'], {'null': 'True', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label','codename')", 'unique_together': "(('content_type','codename'),)"},
            'codename': ('models.CharField', ["_('codename')"], {'max_length': '100'}),
            'content_type': ('models.ForeignKey', ['ContentType'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('name')"], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'events.optiongroup': {
            'description': ('HTMLField', ["_('Description')"], {'blank': 'True'}),
            'event': ('models.ForeignKey', ['Event'], {}),
            'freeze_time': ('models.DateTimeField', ["_('Freeze time')"], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'maximum_attendees': ('models.IntegerField', ["_('Maximum attendees')"], {'default': '0'}),
            'maximum_selected': ('models.IntegerField', ["_('Maximum selected')"], {'default': '0'}),
            'minimum_selected': ('models.IntegerField', ["_('Minimum selected')"], {'default': '0'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '255'}),
            'order': ('models.IntegerField', ["_('Order')"], {'default': '0'})
        },
        'events.option': {
            'description': ('HTMLField', ["_('Description')"], {'blank': 'True'}),
            'freeze_time': ('models.DateTimeField', ["_('Freeze time')"], {'null': 'True', 'blank': 'True'}),
            'group': ('models.ForeignKey', ['OptionGroup'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'maximum_attendees': ('models.IntegerField', ["_('Maximum attendees')"], {'null': 'True', 'blank': 'True'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '255'}),
            'order': ('models.IntegerField', ["_('Order')"], {'default': '0'}),
            'price': ('models.IntegerField', [], {'default': '0'}),
            'users': ('models.ManyToManyField', ['User'], {'blank': 'True'})
        },
        'auth.group': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('name')"], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('models.ManyToManyField', ['Permission'], {'verbose_name': "_('permissions')", 'blank': 'True'})
        }
    }
    
    complete_apps = ['events', 'auth']
