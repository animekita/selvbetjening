from django.forms import ModelForm

from selvbetjening.data.invoice.models import Payment

class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = ('amount', 'note')