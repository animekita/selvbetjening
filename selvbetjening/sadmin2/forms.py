
from decimal import Decimal

from django import forms
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Row, Fieldset
from crispy_forms.bootstrap import Tab, TabHolder

from selvbetjening.core.events.models import Event, AttendState


class S2FormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        horizontal = kwargs.pop('horizontal', False)

        super(S2FormHelper, self).__init__(*args, **kwargs)

        if horizontal:
            self.form_class = 'form-horizontal'
            self.label_class = 'col-lg-2'
            self.field_class = 'col-lg-8'

        self.html5_required = True


class S2Field(Field):
    def __init__(self, *args, **kwargs):
        kwargs['css_class'] = 'input-xxlarge'
        super(S2Field, self).__init__(*args, **kwargs)


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('title', 'description', 'group', 'startdate', 'enddate', 'registration_open',
                  'maximum_attendees', 'move_to_accepted_policy')

    helper = S2FormHelper()

    layout = Layout(
        Fieldset(None,
                 S2Field('title'), S2Field('description'), S2Field('group'),
                 S2Field('startdate'), S2Field('enddate'), S2Field('registration_open')),
        Fieldset(_('Conditions'),
                 S2Field('maximum_attendees'), S2Field('move_to_accepted_policy')))

    submit = Submit('save', _('Save'))

    helper.add_layout(layout)
    helper.add_input(submit)


class EventDisplayForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('show_custom_signup_message', 'custom_signup_message', 'show_custom_change_message',
                  'custom_change_message', 'show_custom_status_page', 'custom_status_page')

    helper = S2FormHelper()

    layout = Layout(
        Fieldset(_('Custom signup message'),
                 S2Field('show_custom_signup_message'), S2Field('custom_signup_message')),
        Fieldset(_('Custom change message'),
                 S2Field('show_custom_change_message'), S2Field('custom_change_message')),
        Fieldset(_('Custom status page'),
                 S2Field('show_custom_status_page'), S2Field('custom_status_page')))

    submit = Submit('save', _('Save'))

    helper.add_layout(layout)
    helper.add_input(submit)


class InvoiceFormattingForm(forms.Form):
    FILTER_ATTENDED_CHOICES = [('all', _('All')),
                               ('only_attended', _('Only attended')),
                               ('not_attended', _('Not attended'))]

    filter_attended = forms.ChoiceField(label=_('Filter attended'), choices=FILTER_ATTENDED_CHOICES)
    show_each_user = forms.BooleanField(label=_('Show a detailed view of each attendee'), required=False)
    exclude_lines = forms.MultipleChoiceField(choices=[], required=False)

    helper = S2FormHelper()

    layout = Layout(
        Fieldset(None,
                 S2Field('filter_attended'), S2Field('show_each_user'), S2Field('exclude_lines')))

    submit = Submit('update', _('Update'))

    helper.add_layout(layout)
    helper.add_input(submit)

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