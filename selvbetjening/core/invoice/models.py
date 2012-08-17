try:
    import thread
except ImportError:
    import dummy_thread as thread

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.db.models.signals import post_save

import signals

_disable_invoice_updates = {}

class InvoiceManager(models.Manager):
    def halt_updates(self):
        thread_ident = thread.get_ident()
        _disable_invoice_updates[thread_ident] = True

    def continue_updates(self):
        thread_ident = thread.get_ident()
        _disable_invoice_updates.pop(thread_ident, None)

class Invoice(models.Model):
    name = models.CharField(max_length=256)
    user = models.ForeignKey(User)
    latest = models.ForeignKey('InvoiceRevision', related_name='latestrevision', null=True, blank=True)

    objects = InvoiceManager()

    @property
    def latest_revision(self):
        if not hasattr(self, '_latest_revision'):
            self._latest_revision = self.latest

            if self._latest_revision is None:
                try:
                    self._latest_revision = self.revision_set.latest('id')
                    self.latest = self._latest_revision
                    self.save()
                except InvoiceRevision.DoesNotExist:
                    self._latest_revision = InvoiceRevision.objects.create(invoice=self)

        return self._latest_revision

    @property
    def line_set(self):
        return self.latest_revision.line_set.all().order_by('group_name', 'pk')

    @property
    def total_price(self):
        return self.latest_revision.total_price

    @property
    def paid(self):
        paid = 0
        for payment in self.payment_set.all():
            paid += payment.amount
        return paid

    @property
    def unpaid(self):
        return self.total_price - self.paid

    @property
    def overpaid(self):
        return self.paid - self.total_price

    @property
    def payment_set(self):
        return Payment.objects.filter(revision__invoice=self)

    def update(self, force=False):
        thread_ident = thread.get_ident()

        if force or \
           thread_ident not in _disable_invoice_updates:

            revision = InvoiceRevision.objects.create(invoice=self)
            signals.populate_invoice.send(self, invoice_revision=revision)

    def is_paid(self):
        return self.paid >= self.total_price
    is_paid.boolean = True

    def in_balance(self):
        return self.paid == self.total_price
    is_paid.boolean = True

    def is_overpaid(self):
        return self.paid > self.total_price
    is_overpaid.boolean = True

    def is_partial(self):
        return self.paid > 0 and not self.is_paid()
    is_partial.boolean = True

    def is_unpaid(self):
        return self.paid == 0 and not self.total_price == 0
    is_unpaid.boolean = True

    def __unicode__(self):
        return self.name

class InvoiceRevision(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='revision_set')
    created_date = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        total = 0
        for line in self.line_set.all():
            total += line.price
        return total

    @property
    def paid(self):
        paid = 0
        for payment in Payment.objects.filter(revision=self):
            paid += payment.amount

        return paid

    @property
    def unpaid(self):
        return self.total_price - self.paid

    @property
    def overpaid(self):
        return self.paid - self.total_price

    def is_paid(self):
        return self.paid >= self.total_price
    is_paid.boolean = True

    def in_balance(self):
        return self.paid == self.total_price
    is_paid.boolean = True

    def is_overpaid(self):
        return self.paid > self.total_price
    is_overpaid.boolean = True

    def is_partial(self):
        return self.paid > 0 and not self.is_paid()
    is_partial.boolean = True

    def is_unpaid(self):
        return self.paid == 0 and not self.total_price == 0
    is_unpaid.boolean = True

    def add_line(self, description, price, managed=False, group_name=None):
        if group_name is None:
            group_name = ''

        return Line.objects.create(revision=self,
                                   description=description,
                                   group_name=group_name,
                                   price=price,
                                   managed=managed)

    def __unicode__(self):
        return u'Invoice as of %s' % self.created_date

def update_revision_pointer(**kwargs):
    created = kwargs['created']
    instance = kwargs['instance']

    if created:
        instance.invoice.latest = instance
        instance.invoice.save()

post_save.connect(update_revision_pointer, InvoiceRevision)


class Line(models.Model):
    revision = models.ForeignKey(InvoiceRevision)
    group_name = models.CharField(max_length=255, default='')
    description = models.CharField(max_length=255)
    managed = models.BooleanField(default=False)
    price = models.DecimalField(default=0, max_digits=6, decimal_places=2)

    def __unicode__(self):
        return self.description

class Payment(models.Model):
    invoice = models.ForeignKey(Invoice)
    created_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    signee = models.ForeignKey(User, null=True, blank=True, related_name='signed_payment_set')
    note = models.CharField(max_length=256, blank=True)


