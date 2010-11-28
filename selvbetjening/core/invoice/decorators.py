from selvbetjening.data.invoice.models import Invoice

def disable_invoice_updates(func):
    def _disable_invoice_updates(*args, **kw):
        try:
            Invoice.objects.halt_updates()

            res = func(*args, **kw)
            return res
        except:
            raise
        finally:
            Invoice.objects.continue_updates()
    return _disable_invoice_updates