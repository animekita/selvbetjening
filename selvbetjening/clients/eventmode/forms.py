from django.forms import ModelForm

from selvbetjening.data.invoice.models import Payment

from models import Note

class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = ('amount', 'note')

class NoteForm(ModelForm):
    class Meta:
        model = Note
        fields = ('title', 'note')
