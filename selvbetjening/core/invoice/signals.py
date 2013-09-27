
from django.dispatch import Signal

populate_invoice = Signal(providing_args=['invoice_revision'])