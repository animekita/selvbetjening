from django.test import TestCase
from django.contrib.auth.models import User

import models

class Database(object):
    _id = 0
    @classmethod
    def new_id(cls):
        cls._id += 1
        return str(cls._id)
    
    @classmethod
    def new_user(cls, id=None):
        if id is None:
            id = cls.new_id()
        return User.objects.create_user(id, '%s@example.org' % id, id)

    @classmethod
    def new_invoice(self, user):
        return models.Invoice.objects.create(name='test', user=user)

    @classmethod
    def pay_invoice(self, invoice):
        models.Payment.objects.create(revision=invoice.latest_revision,
                                      amount=invoice.total_price)
    
class InvoiceModelTestCase(TestCase):
    def test_latest_no_revisions(self):
        user = Database.new_user()
        invoice = Database.new_invoice(user)
        
        revision = invoice.latest_revision
        self.assertEqual(revision, invoice.latest_revision)
        self.assertTrue(isinstance(revision, models.InvoiceRevision))
        
    def test_is_paid_empty(self):
        user = Database.new_user()
        invoice = Database.new_invoice(user)
        
        self.assertTrue(invoice.is_paid())