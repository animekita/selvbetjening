
from south.db import db
from django.db import models
from selvbetjening.core.invoice.models import *

class Migration:

    def forwards(self, orm):

        # Adding field 'Line.managed'
        db.add_column('invoice_line', 'managed', models.BooleanField(default=False))

        # Deleting field 'Invoice.managed'
        db.delete_column('invoice_invoice', 'managed')

        # Deleting field 'Invoice.dropped'
        db.delete_column('invoice_invoice', 'dropped')



    def backwards(self, orm):

        # Deleting field 'Line.managed'
        db.delete_column('invoice_line', 'managed')

        # Adding field 'Invoice.managed'
        db.add_column('invoice_invoice', 'managed', models.BooleanField(default=False))

        # Adding field 'Invoice.dropped'
        db.add_column('invoice_invoice', 'dropped', models.BooleanField(default=False))



    models = {
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'invoice.invoicerevision': {
            'created_date': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('models.ForeignKey', ['Invoice'], {'related_name': "'revision_set'"})
        },
        'invoice.line': {
            'description': ('models.CharField', [], {'max_length': '255'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'managed': ('models.BooleanField', [], {'default': 'False'}),
            'price': ('models.IntegerField', [], {'default': '0'}),
            'revision': ('models.ForeignKey', ['InvoiceRevision'], {})
        },
        'invoice.invoice': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '256'}),
            'user': ('models.ForeignKey', ['User'], {})
        },
        'invoice.payment': {
            'amount': ('models.IntegerField', [], {}),
            'created_date': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'note': ('models.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'revision': ('models.ForeignKey', ['InvoiceRevision'], {}),
            'signee': ('models.ForeignKey', ['User'], {'related_name': "'signed_payment_set'", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['invoice']
