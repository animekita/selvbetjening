# coding=UTF-8

from south.db import db
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from selvbetjening.data.events.models import *

class Migration:

    no_dry_run = True

    depends_on = (
        ("invoice", "0002_corrections"),
    )

    def forwards(self, orm):
        for attendee in orm.Attend.objects.all():
            try:
                invoice = attendee.invoice
                continue
            except ObjectDoesNotExist:
                pass

            invoice = orm['invoice.Invoice'].objects.create(user=attendee.user,
                                                            name='%s' % attendee.event.title)

            invoice_revision = orm['invoice.InvoiceRevision'].objects.create(invoice=invoice)

            for selection in orm.Selection.objects.filter(attendee=attendee):
                orm['invoice.Line'].objects.create(revision=invoice_revision,
                                                   description=u'%s' % selection.option.name,
                                                   price=selection.option.price,
                                                   managed=True)

            attendee.invoice = invoice
            attendee.save()

    def backwards(self, orm):
        "Write your backwards migration here"


    models = {
        'events.event': {
            'change_confirmation': ('models.TextField', [], {'blank': 'True'}),
            'description': ('models.TextField', ["_(u'description')"], {'blank': 'True'}),
            'enddate': ('models.DateField', ["_(u'end date')"], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'maximum_attendees': ('models.IntegerField', ["_('Maximum attendees')"], {'default': '0'}),
            'registration_confirmation': ('models.TextField', [], {'blank': 'True'}),
            'registration_open': ('models.BooleanField', ["_(u'registration open')"], {}),
            'show_change_confirmation': ('models.BooleanField', [], {'default': 'False'}),
            'show_registration_confirmation': ('models.BooleanField', [], {'default': 'False'}),
            'startdate': ('models.DateField', ["_(u'start date')"], {'null': 'True', 'blank': 'True'}),
            'title': ('models.CharField', ["_(u'title')"], {'max_length': '255'})
        },
        'events.suboption': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '255'}),
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
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label','codename')", 'unique_together': "(('content_type','codename'),)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'auth.group': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'invoice.invoice': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '256'}),
            'user': ('models.ForeignKey', ['User'], {})
        },
        'invoice.payment': {
            'amount': ('models.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'created_date': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'note': ('models.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'revision': ('models.ForeignKey', ['InvoiceRevision'], {}),
            'signee': ('models.ForeignKey', ['User'], {'related_name': "'signed_payment_set'", 'null': 'True', 'blank': 'True'})
        },
        'events.selection': {
            'Meta': {'unique_together': "(('attendee','option'))"},
            'attendee': ('models.ForeignKey', ['Attend'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'option': ('models.ForeignKey', ['Option'], {}),
            'suboption': ('models.ForeignKey', ['SubOption'], {'null': 'True', 'blank': 'True'})
        },
        'invoice.invoicerevision': {
            'created_date': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('models.ForeignKey', ['Invoice'], {'related_name': "'revision_set'"})
        },
        'events.optiongroup': {
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
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
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'freeze_time': ('models.DateTimeField', ["_('Freeze time')"], {'null': 'True', 'blank': 'True'}),
            'group': ('models.ForeignKey', ['OptionGroup'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'maximum_attendees': ('models.IntegerField', ["_('Maximum attendees')"], {'null': 'True', 'blank': 'True'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '255'}),
            'order': ('models.IntegerField', ["_('Order')"], {'default': '0'}),
            'price': ('models.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'})
        },
        'invoice.line': {
            'description': ('models.CharField', [], {'max_length': '255'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'managed': ('models.BooleanField', [], {'default': 'False'}),
            'price': ('models.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'revision': ('models.ForeignKey', ['InvoiceRevision'], {})
        }
    }

    complete_apps = ['events', 'invoice']
