from decimal import Decimal

from django import forms
from django.utils.translation import ugettext as _
from django.contrib.admin.widgets import AdminRadioSelect
from django.contrib.auth.models import User

from selvbetjening.data.events.models import Event, AttendState
from selvbetjening.data.invoice.models import Line

from models import Invoice, InvoiceRevision

class InvoiceSourceForm(forms.Form):
    EVENT_CHOICES = [('', '')] + [(event.id, event.title) for event in Event.objects.all()]
    FILTER_ATTENDED_CHOICES = [('all', _('All')),
                               ('only_attended', _('Only attended')),
                               ('not_attended', _('Not attended'))]

    event = forms.ChoiceField(choices=EVENT_CHOICES, required=False)
    filter_attended = forms.ChoiceField(label=_('Filter attended'), choices=FILTER_ATTENDED_CHOICES)

    def filter(self, invoice_queryset):
        event_id = self.cleaned_data.get('event', None)
        if event_id is not None and not event_id == '':
            invoice_queryset = invoice_queryset.filter(attend__event__pk=event_id)

        if self.cleaned_data['filter_attended'] == 'only_attended':
            invoice_queryset = invoice_queryset.filter(attend__state=AttendState.attended)
        elif self.cleaned_data['filter_attended'] == 'not_attended':
            invoice_queryset = invoice_queryset.exclude(attend__state=AttendState.attended)

        return invoice_queryset

class InvoiceFormattingForm(forms.Form):
    exclude_lines = forms.MultipleChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        self.invoices = kwargs.pop('invoices', [])

        super(InvoiceFormattingForm, self).__init__(*args, **kwargs)

        lines = []
        for invoice in self.invoices:
            for line in invoice.line_set.all():
                lines.append(line.description)

        self._all_lines = set(lines)

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

            if line.revision.is_overpaid():
                self.overpaid_total += line.price
                self.overpaid.append(line)
            elif line.revision.in_balance():
                self.paid_total += line.price
                self.paid.append(line)
            elif line.revision.is_partial():
                self.partial_total += line.price
                self.partial.append(line)
            else:
                self.unpaid_total += line.price
                self.unpaid.append(line)

            self.total = self.overpaid_total + self.paid_total + self.partial_total + self.unpaid_total

    def format(self, invoices):
        line_groups = {}

        for invoice in self.invoices:
            for line in invoice.line_set.all():
                if line.description in self.lines:
                    if not line_groups.has_key(line.description):
                        line_groups[line.description] = self.LineGroup(line.description)

                    line_groups[line.description].add(line)

        return [line_groups[id] for id in line_groups]

class InvoiceGlobalIdForm(forms.Form):
    revision_id = forms.IntegerField()
    invoice_id = forms.IntegerField()
    user_id = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        self.revision = None
        self.invoice = None
        self.user = None

        super(InvoiceGlobalIdForm, self).__init__(*args, **kwargs)

    def clean_revision_id(self):
        revision_id = self.cleaned_data['revision_id']

        try:
            self.revision = InvoiceRevision.objects.get(pk=revision_id)
        except InvoiceRevision.DoesNotExist:
            raise forms.ValidationError(u'Invoice revision does not exist')

        return revision_id

    def clean_invoice_id(self):
        invoice_id = self.cleaned_data['invoice_id']

        try:
            self.invoice = Invoice.objects.get(pk=invoice_id)
        except Invoice.DoesNotExist:
            raise forms.ValidationError(u'Invoice does not exist')

        return invoice_id

    def clean_user_id(self):
        user_id = self.cleaned_data['user_id']

        try:
            self.user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise forms.ValidationError(u'User does not exist')

        return user_id

    def clean(self):

        if self.invoice is not None and self.invoice.user != self.user:
            raise forms.ValidationError('Invoice and user does not match')

        if self.revision is not None and self.revision.invoice != self.invoice:
            raise forms.ValidationError('Invoice and invoice revision does not match')

        return self.cleaned_data
