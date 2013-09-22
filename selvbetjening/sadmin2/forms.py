
from decimal import Decimal
from collections import OrderedDict

from django import forms
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.forms.extras.widgets import SelectDateWidget

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Row, Fieldset, Div, HTML

from selvbetjening.core.invoice.models import Payment
from selvbetjening.core.events.models import Event, AttendState, find_attendee_signal, OptionGroup, Option, AttendeeComment
from selvbetjening.core.invoice.utils import sum_invoices


class S2FormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        horizontal = kwargs.pop('horizontal', False)

        super(S2FormHelper, self).__init__(*args, **kwargs)

        if horizontal:
            self.form_class = 'form-horizontal'
            self.label_class = 'col-lg-2'
            self.field_class = 'col-lg-8'

        self.html5_required = True


class S2Layout(Layout):

    template = "sadmin2/generic/parts/form_layout.html"

    def render(self, *args, **kwargs):

        fields = super(S2Layout, self).render(*args, **kwargs)

        return render_to_string(self.template, {'layout': self, 'fields': fields})


class S2Field(Field):
    def __init__(self, *args, **kwargs):

        kwargs['css_class'] = kwargs.get('css_class', '') + ' input-lg'

        if 'width' in kwargs:
            kwargs['wrapper_class'] = kwargs.get('wrapper_class', '') + ' col-lg-%s' % kwargs.get('width')

        super(S2Field, self).__init__(*args, **kwargs)


class S2Fieldset(Fieldset):

    template = "sadmin2/generic/parts/form_fieldset.html"

    def __init__(self, name, *args, **kwargs):

        args = [(S2Field(arg) if isinstance(arg, str) else arg) for arg in args]
        super(S2Fieldset, self).__init__(name, *args, **kwargs)


class S2HorizontalRow(Row):
    def __init__(self, *args, **kwargs):
        """
        Formatting of inlined elements in horizontal rows is not pretty. Lets apply some col-lg-* hacking.

        - Add a col-lg-2 to offset left-hand-side labels
        - Add a col-lg-9 representing the useful span (avoiding the right-hand-side padding)

        We add given fields to this second div.

        """

        super(S2HorizontalRow, self).__init__(Div(css_class='col-lg-2'), Div(*args, css_class='col-lg-9'), **kwargs)


class S2Submit(Submit):
    def __init__(self, *args, **kwargs):
        kwargs['css_class'] = kwargs.get('css_class', '') + ' btn-lg'
        super(S2Submit, self).__init__(*args, **kwargs)


class S2SubmitCreate(S2Submit):

    def __init__(self):
        super(S2Submit, self).__init__('create', _('Create'))


class S2SubmitUpdate(S2Submit):

    def __init__(self):
        super(S2Submit, self).__init__('update', _('Update'))


from django.forms.widgets import TextInput


class SplitDateWidget(SelectDateWidget):

    def create_select(self, name, field, value, val, choices):
        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name

        #if not (self.required and val):

        local_attrs = self.build_attrs(id=field % id_)
        local_attrs['width'] = 2

        s = TextInput()
        select_html = s.render(field % name, val, local_attrs)

        if 'day' in field:
            label = 'dd'
        elif 'month' in field:
            label = 'mm'
        else:
            label = 'yyyy'

        html = \
            """
            <div class="input-group col-lg-4">
                <span class="input-group-addon">%s</span>
                %s
            </div>
            """ % (label, select_html)

        return html


class EventForm(forms.ModelForm):
    class Meta:
        model = Event

        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'startdate': SplitDateWidget(),
            'enddate': SplitDateWidget()
        }

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)

        self.helper = S2FormHelper(horizontal=True)

        layout = S2Layout(
            S2Fieldset(None,
                       'title', 'description', 'group',
                       'startdate', 'enddate',
                       'registration_open'),
            S2Fieldset(_('Conditions'),
                       'maximum_attendees', 'move_to_accepted_policy'),
            S2Fieldset(_('Feedback'),
                       'show_custom_signup_message', 'custom_signup_message',
                       'show_custom_change_message', 'custom_change_message',
                       'show_custom_status_page', 'custom_status_page'))

        self.helper.add_layout(layout)
        self.helper.add_input(S2SubmitUpdate() if 'instance' in kwargs else S2SubmitCreate())


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

        if not hasattr(self, 'cleaned_data'):
            self.cleaned_data = {}

        # Defaults

        attendee_filter_label = self.FILTER_ATTENDED_CHOICES[0][1]
        attendee_filter = self.cleaned_data.get('filter_attended', 'attended_or_paid')

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

        show_each_user = self.cleaned_data.get('show_each_user', 'over_and_under')

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

        for invoice in self.invoices:

            for line in invoice.line_set.all():
                key = self._get_distinct_line_name(line)

                if key in self.distinct_lines:
                    line_groups[key].add(line)

        total = sum_invoices(self.invoices)

        return self.invoices, line_groups.values(), total, show_regular_attendees, show_irregular_attendees, attendee_filter_label


class RegisterPaymentForm(forms.Form):
    payment_key = forms.CharField(max_length=255)
    payment = forms.DecimalField(decimal_places=2)

    fieldsets = [
        (None, {
            'fields': ('payment_key', 'payment'),
        })
    ]

    helper = S2FormHelper(horizontal=True)

    layout = Layout(
        Fieldset(None,
                 S2Field('payment_key'), S2Field('payment')))

    submit = Submit('update', _('Register'))

    helper.add_layout(layout)
    helper.add_input(submit)

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


class OptionGroupForm(forms.ModelForm):
    class Meta:
        model = OptionGroup
        exclude = ('event', 'order')

        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super(OptionGroupForm, self).__init__(*args, **kwargs)

        self.helper = S2FormHelper(horizontal=True)

        layout = S2Layout(
            S2Fieldset(None,
                       S2Field('name'), S2Field('description')),
            S2Fieldset(_('Conditions'),
                       'minimum_selected', 'maximum_selected', 'maximum_attendees', 'freeze_time', 'lock_selections_on_acceptance'),
            S2Fieldset(_('Package'),
                       'package_solution', 'package_price'),
            S2Fieldset(_('Display'),
                       'public_statistic'))

        self.helper.add_layout(layout)
        self.helper.add_input(S2SubmitUpdate() if 'instance' in kwargs else S2SubmitCreate())


class OptionForm(forms.ModelForm):

    class Meta:
        model = Option
        exclude = ('group', 'order')

        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):

        super(OptionForm, self).__init__(*args, **kwargs)

        self.helper = S2FormHelper(horizontal=True)

        layout = S2Layout(
            S2Fieldset(None,
                       'name', 'description', 'price'),
            S2Fieldset(_('Conditions'),
                       'freeze_time', 'maximum_attendees'))

        self.helper.add_layout(layout)
        self.helper.add_input(S2SubmitUpdate() if 'instance' in kwargs else S2SubmitCreate())


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ('amount',)

    helper = S2FormHelper(horizontal=True)

    layout = S2Layout(
        S2Fieldset(None, 'amount')
    )

    helper.add_layout(layout)
    helper.add_input(S2Submit('pay', _('Pay')))


class AttendeeCommentForm(forms.ModelForm):
    class Meta:
        model = AttendeeComment
        fields = ('comment',)

        widgets = {
            'comment': forms.Textarea(attrs={'rows': 2}),
        }

    helper = S2FormHelper(horizontal=True)

    layout = S2Layout(
        S2Fieldset(None, 'comment')
    )

    helper.add_layout(layout)
    helper.add_input(S2SubmitCreate())