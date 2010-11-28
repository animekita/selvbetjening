
from south.db import db
from django.db import models
from selvbetjening.data.invoice.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'InvoicePaymentWorkflow'
        db.create_table('invoice_invoicepaymentworkflow', (
            ('id', orm['invoice.invoicepaymentworkflow:id']),
            ('name', orm['invoice.invoicepaymentworkflow:name']),
            ('notification_email_subject', orm['invoice.invoicepaymentworkflow:notification_email_subject']),
            ('notification_email', orm['invoice.invoicepaymentworkflow:notification_email']),
        ))
        db.send_create_signal('invoice', ['InvoicePaymentWorkflow'])
        
        # Changing field 'InvoiceRevision.created_date'
        # (to signature: django.db.models.fields.DateTimeField(auto_now_add=True, blank=True))
        db.alter_column('invoice_invoicerevision', 'created_date', orm['invoice.invoicerevision:created_date'])
        
        # Changing field 'Line.managed'
        # (to signature: django.db.models.fields.BooleanField(blank=True))
        db.alter_column('invoice_line', 'managed', orm['invoice.line:managed'])
        
        # Changing field 'Payment.created_date'
        # (to signature: django.db.models.fields.DateTimeField(auto_now_add=True, blank=True))
        db.alter_column('invoice_payment', 'created_date', orm['invoice.payment:created_date'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'InvoicePaymentWorkflow'
        db.delete_table('invoice_invoicepaymentworkflow')
        
        # Changing field 'InvoiceRevision.created_date'
        # (to signature: models.DateTimeField(auto_now_add=True))
        db.alter_column('invoice_invoicerevision', 'created_date', orm['invoice.invoicerevision:created_date'])
        
        # Changing field 'Line.managed'
        # (to signature: models.BooleanField())
        db.alter_column('invoice_line', 'managed', orm['invoice.line:managed'])
        
        # Changing field 'Payment.created_date'
        # (to signature: models.DateTimeField(auto_now_add=True))
        db.alter_column('invoice_payment', 'created_date', orm['invoice.payment:created_date'])
        
    
    
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
        'invoice.invoice': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'invoice.invoicepaymentworkflow': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'notification_email': ('django.db.models.fields.TextField', [], {}),
            'notification_email_subject': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'invoice.invoicerevision': {
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'revision_set'", 'to': "orm['invoice.Invoice']"})
        },
        'invoice.line': {
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'managed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'revision': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['invoice.InvoiceRevision']"})
        },
        'invoice.payment': {
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'revision': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['invoice.InvoiceRevision']"}),
            'signee': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'signed_payment_set'", 'null': 'True', 'to': "orm['auth.User']"})
        }
    }
    
    complete_apps = ['invoice']
