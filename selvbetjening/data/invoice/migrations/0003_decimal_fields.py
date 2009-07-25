
from south.db import db
from django.db import models
from selvbetjening.data.invoice.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Changing field 'Line.price'
        db.alter_column('invoice_line', 'price', models.DecimalField(default=0, max_digits=6, decimal_places=2))
        
        # Changing field 'Payment.amount'
        db.alter_column('invoice_payment', 'amount', models.DecimalField(max_digits=6, decimal_places=2))
        
    
    
    def backwards(self, orm):
        
        # Changing field 'Line.price'
        db.alter_column('invoice_line', 'price', models.IntegerField(default=0))
        
        # Changing field 'Payment.amount'
        db.alter_column('invoice_payment', 'amount', models.IntegerField())
        
    
    
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
            'price': ('models.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'revision': ('models.ForeignKey', ['InvoiceRevision'], {})
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
        }
    }
    
    complete_apps = ['invoice']
