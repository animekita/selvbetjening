from decimal import Decimal

from django import forms
from django.contrib.admin.widgets import AdminRadioSelect

from selvbetjening.data.events.models import Event
from selvbetjening.data.invoice.models import Line

class InvoiceSourceForm(forms.Form):
    EVENT_CHOICES = [('', '')] + [(event.id, event.title) for event in Event.objects.all()]

    event = forms.ChoiceField(choices=EVENT_CHOICES, required=False)

    def filter(self, queryset):
        event_id = self.cleaned_data.get('event', None)
        if event_id is not None and not event_id == '':
            queryset = queryset.filter(attend__event__pk=event_id)

        return queryset

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


