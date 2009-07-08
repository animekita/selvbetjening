from django.db import models
from django.contrib.auth.models import User

class Invoice(models.Model):
    name = models.CharField(max_length=256)
    dropped = models.BooleanField(default=False)
    user = models.ForeignKey(User)

    @property
    def latest_revision(self):
        if self.revision_set.count() == 0:
            return InvoiceRevision.objects.create(invoice=self)
        else:
            return self.revision_set.latest('created_date')
        
class InvoiceRevision(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='revision_set')
    created_date = models.DateTimeField(auto_now_add=True)
        
class Line(models.Model):
    revision = models.ForeignKey(InvoiceRevision)
    description = models.CharField(max_length=255)
    price = models.IntegerField(default=0)

class Payment(models.Model):
    revision = models.ForeignKey(InvoiceRevision)
    created_date = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    signee = models.ForeignKey(User, null=True, blank=True, related_name='signed_payment_set')
    note = models.CharField(max_length=256, blank=True)

