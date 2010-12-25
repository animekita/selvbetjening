from decimal import Decimal

from django import forms
from django.utils.translation import ugettext as _

from uni_form.helpers import FormHelper, Submit

from selvbetjening.viewbase.forms.helpers import InlineFieldset

from selvbetjening.core.events.models import Event, AttendState, Attend, find_attendee_signal
from selvbetjening.core.invoice.models import Payment

class InvoiceFormattingForm(forms.Form):
    FILTER_ATTENDED_CHOICES = [('all', _('All')),
                               ('only_attended', _('Only attended')),
                               ('not_attended', _('Not attended'))]

    filter_attended = forms.ChoiceField(label=_('Filter attended'), choices=FILTER_ATTENDED_CHOICES)
    exclude_lines = forms.MultipleChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        self.invoices = kwargs.pop('invoices', [])

        super(InvoiceFormattingForm, self).__init__(*args, **kwargs)

        lines = []
        for invoice in self.invoices:
            for line in invoice.line_set.all():
                lines.append(line.description)



        self._all_lines = sorted(set(lines), key=lambda k: k)
        self.lines = self._all_lines

        self.fields['exclude_lines'].choices = [(line, line) for line in self._all_lines]   
        
    def clean(self):
        self.lines = set(self._all_lines).difference(set(self.cleaned_data.get('exclude_lines', [])))

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

        def add(self, line):
            self.lines.append(line)
            
            invoice = line.revision.invoice

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
        if hasattr(self, 'cleaned_data'):
            if self.cleaned_data['filter_attended'] == 'only_attended':
                self.invoices = self.invoices.filter(attend__state=AttendState.attended)
            elif self.cleaned_data['filter_attended'] == 'not_attended':
                self.invoices = self.invoices.exclude(attend__state=AttendState.attended)
        
        line_groups = {}

        for invoice in self.invoices:
            for line in invoice.line_set.all():
                if line.description in self.lines:
                    if not line_groups.has_key(line.description):
                        line_groups[line.description] = self.LineGroup(line.description)

                    line_groups[line.description].add(line)

        total = {'overpaid': 0, 'paid': 0, 'partial': 0, 'unpaid': 0, 'total': 0}
        for id in line_groups:
            line_group = line_groups[id]
            total['overpaid'] += line_group.overpaid_total
            total['paid'] += line_group.paid_total
            total['partial'] += line_group.partial_total
            total['unpaid'] += line_group.unpaid_total
            total['total'] += line_group.total

        return sorted([line_groups[id] for id in line_groups], key=lambda i: i.name), total

class CheckinForm(forms.Form):
    def __init__(self, *args, **kwargs):

        attendee = kwargs.pop('attendee')
        helper = FormHelper()
        helper.add_layout(InlineFieldset(None))
        helper.form_tag = True
        helper.use_csrf_protection = True

        if attendee.state == AttendState.attended:
            checkout = Submit(_('Checkout'), _('Checkout'))
            helper.add_input(checkout)
        else:
            checkin_and_pay = Submit(_('Checkin and Pay'), _('Checkin and Pay'))
            checkin = Submit(_('Checkin only'), _('Checkin only'))
            helper.add_input(checkin_and_pay)
            helper.add_input(checkin)

        self.helper = helper

        super(CheckinForm, self).__init__(*args, **kwargs)
        
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        
    fieldsets = [
        (None, {
            'fields': (('amount', 'note'),)
        })
    ]
    
class AttendeeForm(forms.ModelForm):
    class Meta:
        model = Attend
        fields = ('state',)
        
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
        
        self.attendees = results
        
        return payment_key