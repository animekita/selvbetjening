from decimal import Decimal

from django import forms
from django.utils.translation import ugettext as _

from selvbetjening.core.events.models import AttendState, find_attendee_signal
from selvbetjening.core.invoice.models import Payment


class InvoiceFormattingForm(forms.Form):
    FILTER_ATTENDED_CHOICES = [('all', _('All')),
                               ('only_attended', _('Only attended')),
                               ('not_attended', _('Not attended'))]

    filter_attended = forms.ChoiceField(label=_('Filter attended'), choices=FILTER_ATTENDED_CHOICES)
    show_each_user = forms.BooleanField(label=_('Show a detailed view of each attendee'), required=False)
    exclude_lines = forms.MultipleChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        self.invoices = kwargs.pop('invoices', [])

        super(InvoiceFormattingForm, self).__init__(*args, **kwargs)

        self.all_line_descriptions = []

        for invoice in self.invoices:
            for line in invoice.line_set.all():
                self.all_line_descriptions.append(line.description)

        self.all_line_descriptions = sorted(set(self.all_line_descriptions), key=lambda k: k)

        self.fields['exclude_lines'].choices = [(line, line) for line in self.all_line_descriptions]

    def clean(self):
        self.all_line_descriptions = set(self.all_line_descriptions)\
            .difference(set(self.cleaned_data.get('exclude_lines', [])))

        return self.cleaned_data

    class LineGroup(object):
        def __init__(self, name):
            self.name = name
            self.lines = []

            self.overpaid = []
            self.overpaid_total = Decimal('0.00')

            self.paid = []
            self.paid_total = Decimal('0.00')

            self.partial = []
            self.partial_total = Decimal('0.00')

            self.unpaid = []
            self.unpaid_total = Decimal('0.00')

            self.total = Decimal('0.00')

        def add(self, line, invoice):
            self.lines.append(line)

            if invoice.is_overpaid():
                self.overpaid_total += line.price
                self.overpaid.append(line)
            elif invoice.in_balance():
                self.paid_total += line.price
                self.paid.append(line)
            elif invoice.is_partial():
                self.partial_total += line.price
                self.partial.append(line)
            else:
                self.unpaid_total += line.price
                self.unpaid.append(line)

            self.total = self.overpaid_total + self.paid_total + self.partial_total + self.unpaid_total

    def format(self):
        show_each_user = False

        if hasattr(self, 'cleaned_data'):
            if self.cleaned_data['filter_attended'] == 'only_attended':
                self.invoices = self.invoices.filter(attend__state=AttendState.attended)
            elif self.cleaned_data['filter_attended'] == 'not_attended':
                self.invoices = self.invoices.exclude(attend__state=AttendState.attended)

            show_each_user = self.cleaned_data.get('show_each_user', False)

        line_groups = {}

        for description in self.all_line_descriptions:
            line_groups[description] = self.LineGroup(description)

        for invoice in self.invoices:
            for line in invoice.line_set.all():
                if line.description in self.all_line_descriptions:
                    line_groups[line.description].add(line, invoice)

        total = {'overpaid': 0, 'paid': 0, 'partial': 0, 'unpaid': 0, 'total': 0}
        for key in line_groups:
            line_group = line_groups[key]
            total['overpaid'] += line_group.overpaid_total
            total['paid'] += line_group.paid_total
            total['partial'] += line_group.partial_total
            total['unpaid'] += line_group.unpaid_total
            total['total'] += line_group.total

        return sorted([line_groups[key] for key in line_groups], key=lambda i: i.name), total, show_each_user


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ('amount', 'note')
        
    fieldsets = [
        (None, {
            'fields': (('amount', 'note'),)
        })
    ]


class RegisterPaymentForm(forms.Form):
    payment_key = forms.CharField(max_length=255)
    payment = forms.DecimalField(decimal_places=2)

    fieldsets = [
        (None, {
            'fields': ('payment_key', 'payment'),
         })
    ]
    
    def clean_payment_key(self):
        payment_key = self.cleaned_data['payment_key']

        results = find_attendee_signal.send(self, pk=payment_key)
        results = [result for handler, result in results if result is not None]
        
        if len(results) == 0:
            raise forms.ValidationError(u'No matching payment keys found')
        
        if len(results) > 1:
            raise forms.ValidationError(u'Multiple matching payment keys found')
        
        self.cleaned_data['handler'] = results[0][0]
        self.cleaned_data['attendee'] = results[0][1]
        
        return payment_key