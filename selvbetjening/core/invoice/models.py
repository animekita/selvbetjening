try:
    import thread
except ImportError:
    import dummy_thread as thread

from django.db import models
from django.contrib.auth.models import User

import signals

_disable_invoice_updates = {}


class InvoiceManager(models.Manager):
    def halt_updates(self):
        _disable_invoice_updates[thread.get_ident()] = True

    def continue_updates(self):
        _disable_invoice_updates.pop(thread.get_ident(), None)


class Invoice(models.Model):
    name = models.CharField(max_length=256)
    user = models.ForeignKey(User)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    total_price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    paid = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    objects = InvoiceManager()

    @property
    def invoice(self):
        """
        Backwards compatibility with old InvoiceRevision
        """
        return self

    @property
    def latest_revision(self):
        try:
            return self.revision_set.latest('id')
        except InvoiceRevision.DoesNotExist:
            self.update()
            return self.revision_set.latest('id')

    @property
    def line_set_ordered(self):
        return self.line_set.all().order_by('group_name', 'pk')

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

        self.total_price += price

        return InvoiceLine.objects.create(invoice=self,
                                          description=description,
                                          group_name=group_name,
                                          price=price,
                                          managed=managed)

    def update(self, force=False):
        """
        Save the current state into an invoice revision, and emit a signal that will
        prompt all interested parties to update this invoice with new values.
        """

        if thread.get_ident() in _disable_invoice_updates and not force:
            return

        revision = InvoiceRevision.objects.create(invoice=self,
                                                  total_price=self.total_price)

        for line in self.line_set.all():
            Line.objects.create(revision=revision,
                                group_name=line.group_name,
                                description=line.description,
                                managed=line.managed,
                                price=line.price)

        self.total_price = 0
        self.line_set.all().delete()

        signals.populate_invoice.send(self, invoice=self)

        self.save()

    def __unicode__(self):
        return self.name


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='line_set')
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

    def save(self, *args, **kwargs):
        self.invoice.paid += self.amount
        self.invoice.save()
        super(Payment, self).save(*args, **kwargs)


class InvoiceRevision(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='revision_set')
    created_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __unicode__(self):
        return u'Invoice as of %s' % self.created_date


class Line(models.Model):
    revision = models.ForeignKey(InvoiceRevision, related_name='line_set')
    group_name = models.CharField(max_length=255, default='')
    description = models.CharField(max_length=255)
    managed = models.BooleanField(default=False)
    price = models.DecimalField(default=0, max_digits=6, decimal_places=2)

    def __unicode__(self):
        return self.description
