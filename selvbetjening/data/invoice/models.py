from django.db import models
from django.contrib.auth.models import User

class Invoice(models.Model):
    name = models.CharField(max_length=256)
    dropped = models.BooleanField(default=False)
    managed = models.BooleanField(default=False)
    user = models.ForeignKey(User)

    @property
    def latest_revision(self):
        if self.revision_set.count() == 0:
            return InvoiceRevision.objects.create(invoice=self)
        else:
            return self.revision_set.latest('created_date')

    @property
    def total_price(self):
        total = 0
        for line in self.latest_revision.line_set.all():
            total += line.price
        return total
    
    @property
    def paid(self):
        paid = 0
        for payment in Payment.objects.filter(revision__invoice=self):
            paid += payment.price
            
        return paid
    
    def is_paid(self):
        return self.paid == self.total_price
    is_paid.boolean = True
        
    def create_new_revision(self):
        return InvoiceRevision.objects.create(invoice=self)
    
    def __unicode__(self):
        return self.name
        
class InvoiceRevision(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='revision_set')
    created_date = models.DateTimeField(auto_now_add=True)
    
    def add_line(self, description, price):
        return Line.objects.create(revision=self,
                                   description=description,
                                   price=price)
    
    def __unicode__(self):
        return u'Invoice as of %s' % self.created_date
        
class Line(models.Model):
    revision = models.ForeignKey(InvoiceRevision)
    description = models.CharField(max_length=255)
    price = models.IntegerField(default=0)
    
    def __unicode__(self):
        return self.description

class Payment(models.Model):
    revision = models.ForeignKey(InvoiceRevision)
    created_date = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    signee = models.ForeignKey(User, null=True, blank=True, related_name='signed_payment_set')
    note = models.CharField(max_length=256, blank=True)

