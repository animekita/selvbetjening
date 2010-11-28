
from south.db import db
from django.db import models
from selvbetjening.data.invoice.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'InvoiceRevision'
        db.create_table('invoice_invoicerevision', (
            ('id', models.AutoField(primary_key=True)),
            ('invoice', models.ForeignKey(orm.Invoice, related_name='revision_set')),
            ('created_date', models.DateTimeField(auto_now_add=True)),
        ))
        db.send_create_signal('invoice', ['InvoiceRevision'])
        
        # Adding model 'Line'
        db.create_table('invoice_line', (
            ('price', models.IntegerField(default=0)),
            ('description', models.CharField(max_length=255)),
            ('id', models.AutoField(primary_key=True)),
            ('revision', models.ForeignKey(orm.InvoiceRevision)),
        ))
        db.send_create_signal('invoice', ['Line'])
        
        # Adding model 'Invoice'
        db.create_table('invoice_invoice', (
            ('dropped', models.BooleanField(default=False)),
            ('user', models.ForeignKey(orm['auth.User'])),
            ('managed', models.BooleanField(default=False)),
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(max_length=256)),
        ))
        db.send_create_signal('invoice', ['Invoice'])
        
        # Adding model 'Payment'
        db.create_table('invoice_payment', (
            ('signee', models.ForeignKey(orm['auth.User'], related_name='signed_payment_set', null=True, blank=True)),
            ('note', models.CharField(max_length=256, blank=True)),
            ('amount', models.IntegerField()),
            ('created_date', models.DateTimeField(auto_now_add=True)),
            ('id', models.AutoField(primary_key=True)),
            ('revision', models.ForeignKey(orm.InvoiceRevision)),
        ))
        db.send_create_signal('invoice', ['Payment'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'InvoiceRevision'
        db.delete_table('invoice_invoicerevision')
        
        # Deleting model 'Line'
        db.delete_table('invoice_line')
        
        # Deleting model 'Invoice'
        db.delete_table('invoice_invoice')
        
        # Deleting model 'Payment'
        db.delete_table('invoice_payment')
        
    
    
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
            'price': ('models.IntegerField', [], {'default': '0'}),
            'revision': ('models.ForeignKey', ['InvoiceRevision'], {})
        },
        'invoice.invoice': {
            'dropped': ('models.BooleanField', [], {'default': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'managed': ('models.BooleanField', [], {'default': 'False'}),
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
