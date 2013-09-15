
from decimal import Decimal
from collections import OrderedDict

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
    FILTER_ATTENDED_CHOICES = [('attended_or_paid', _('Attended or has paid')),
                               ('all', _('All')),
                               ('only_attended', _('Only attended')),
                               ('not_attended', _('Not attended'))]

    FILTER_DETAIL_CHOICES = [('over_and_under', _('List attendees (under- and over-paid only)')),
                             ('all', _('List attendees')),
                             ('none', _('Hide attendees'))]

    filter_attended = forms.ChoiceField(label=_('Filter attended'), choices=FILTER_ATTENDED_CHOICES)
    show_each_user = forms.ChoiceField(label=_('List attendees'), choices=FILTER_DETAIL_CHOICES)
    exclude_lines = forms.MultipleChoiceField(choices=[], required=False)

    helper = S2FormHelper(horizontal=True)

    layout = Layout(
        Fieldset(None,
                 S2Field('filter_attended'), S2Field('show_each_user'), S2Field('exclude_lines')))

    submit = Submit('update', _('Generate Account'))

    helper.add_layout(layout)
    helper.add_input(submit)

    def __init__(self, *args, **kwargs):
        self.invoices = kwargs.pop('invoices', [])

        super(InvoiceFormattingForm, self).__init__(*args, **kwargs)

        self.distinct_lines = OrderedDict()

        for invoice in self.invoices:
            for line in invoice.line_set.all():
                self.distinct_lines[self._get_distinct_line_name(line)] = (line.description, line.price)

        self.fields['exclude_lines'].choices = [(line, line) for line in self.distinct_lines.keys()]

    def _get_distinct_line_name(self, line):
        if line.price > 0:
            return '%s (%s,-)' % (line.description, line.price)
        else:
            return line.description

    def clean(self):
        for line in self.cleaned_data.get('exclude_lines', []):
            del self.distinct_lines[line]

        return self.cleaned_data

    class LineGroup(object):
        def __init__(self, name, price):
            self.name = name
            self.price = price

            self.potential = []
            self.potential_total = Decimal('0.00')

        def add(self, line):
            self.potential.append(line)
            self.potential_total += self.price

    def format(self):

        # Defaults

        show_regular_attendees = False
        show_irregular_attendees = True
        attendee_filter_label = self.FILTER_ATTENDED_CHOICES[0][1]

        if hasattr(self, 'cleaned_data'):

            attendee_filter = self.cleaned_data['filter_attended']

            # set attendee label
            for line in self.FILTER_ATTENDED_CHOICES:
                if attendee_filter == line[0]:
                    attendee_filter_label = line[1]

            # filter invoice
            if attendee_filter == 'only_attended':
                self.invoices = self.invoices.filter(attend__state=AttendState.attended)
            elif attendee_filter == 'not_attended':
                self.invoices = self.invoices.exclude(attend__state=AttendState.attended)
            elif attendee_filter == 'attended_or_paid':
                self.invoices = self.invoices.filter(attend__state=AttendState.attended).filter(paid__gt=0)
            elif attendee_filter == 'all':
                pass
            else:
                raise ValueError

            show_each_user = self.cleaned_data.get('show_each_user', None)

            if show_each_user == 'over_and_under':
                show_regular_attendees = False
                show_irregular_attendees = True
            elif show_each_user == 'all':
                show_regular_attendees = True
                show_irregular_attendees = True
            elif show_each_user == 'none':
                show_regular_attendees = False
                show_irregular_attendees = False
            else:
                raise ValueError

        # Initialize empty line groups
        line_groups = OrderedDict()

        for key in self.distinct_lines:
            line = self.distinct_lines[key]
            line_groups[key] = self.LineGroup(line[0], line[1])

        # Initialize base values for all totals
        total = {'potential': 0, 'potential_total': 0,
                 'overpaid': 0, 'overpaid_total': 0,
                 'underpaid': 0, 'underpaid_total': 0,
                 'unpaid': 0, 'unpaid_total': 0,
                 'realised': 0, 'realised_total': 0}

        for invoice in self.invoices:

            for line in invoice.line_set.all():
                key = self._get_distinct_line_name(line)

                if key in self.distinct_lines:
                    line_groups[key].add(line)

            total['potential_total'] += invoice.total_price
            total['potential'] += 1

            if invoice.is_overpaid():
                total['overpaid_total'] += invoice.overpaid
                total['overpaid'] += 1

            elif invoice.is_partial():
                total['underpaid_total'] += invoice.unpaid
                total['underpaid'] += 1

            elif invoice.is_unpaid():
                total['unpaid_total'] += invoice.unpaid
                total['unpaid'] += 1

            total['realised_total'] += invoice.paid
            total['realised'] += 1 if not invoice.is_unpaid() else 0

        return self.invoices, line_groups.values(), total, show_regular_attendees, show_irregular_attendees, attendee_filter_label
