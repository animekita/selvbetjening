# coding=UTF-8

from south.db import db
from django.db import models
from selvbetjening.core.events.models import *

class Migration:

    def forwards(self, orm):

        # Adding model 'Option'
        db.create_table('events_option', (
            ('freeze_time', models.DateTimeField(_('Freeze time'), null=True, blank=True)),
            ('description', models.TextField(_('Description'), blank=True)),
            ('order', models.IntegerField(_('Order'))),
            ('maximum_attendees', models.IntegerField(_('Maximum attendees'), null=True, blank=True)),
            ('group', models.ForeignKey(orm.OptionGroup)),
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(_('Name'), max_length=255)),
        ))
        db.send_create_signal('events', ['Option'])

        # Adding model 'Event'
        db.create_table('events_event', (
            ('startdate', models.DateField(_(u'start date'), null=True, blank=True)),
            ('enddate', models.DateField(_(u'end date'), null=True, blank=True)),
            ('description', models.TextField(_(u'description'), blank=True)),
            ('title', models.CharField(_(u'title'), max_length=255)),
            ('registration_open', models.BooleanField(_(u'registration open'))),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('events', ['Event'])

        # Adding model 'Attend'
        db.create_table('events_attend', (
            ('user', models.ForeignKey(orm['auth.User'])),
            ('has_attended', models.BooleanField()),
            ('id', models.AutoField(primary_key=True)),
            ('event', models.ForeignKey(orm.Event)),
        ))
        db.send_create_signal('events', ['Attend'])

        # Adding model 'OptionGroup'
        db.create_table('events_optiongroup', (
            ('description', models.TextField(_('Description'), blank=True)),
            ('minimum_selected', models.IntegerField(_('Minimum selected'))),
            ('event', models.ForeignKey(orm.Event)),
            ('maximum_attendees', models.IntegerField(_('Maximum attendees'))),
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(_('Name'), max_length=255)),
        ))
        db.send_create_signal('events', ['OptionGroup'])

        # Adding ManyToManyField 'Option.users'
        db.create_table('events_option_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('option', models.ForeignKey(Option, null=False)),
            ('user', models.ForeignKey(User, null=False))
        ))



    def backwards(self, orm):

        # Deleting model 'Option'
        db.delete_table('events_option')

        # Deleting model 'Event'
        db.delete_table('events_event')

        # Deleting model 'Attend'
        db.delete_table('events_attend')

        # Deleting model 'OptionGroup'
        db.delete_table('events_optiongroup')

        # Dropping ManyToManyField 'Option.users'
        db.delete_table('events_option_users')



    models = {
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'events.event': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'events.option': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'events.optiongroup': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }


