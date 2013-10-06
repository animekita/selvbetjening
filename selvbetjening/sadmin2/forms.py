
from decimal import Decimal
from collections import OrderedDict

from django import forms
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _

from crispy_forms.layout import Submit, Layout, Fieldset, HTML
from core.events.models import Selection
from core.events.utils import sum_attendee_payment_status
from core.members.models import UserProfile

from selvbetjening.core.events.models import Event, AttendState, find_attendee_signal, OptionGroup, Option, \
    AttendeeComment, Payment

from selvbetjening.frontend.utilities.forms import *


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


class AttendeeFormattingForm(forms.Form):
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
        self.event = kwargs.pop('event')
        self.attendees = kwargs.pop('attendees').select_related('user')
        self.options = Option.objects.filter(group__event=self.event).order_by('-group__is_special', 'group__order', 'order')

        super(AttendeeFormattingForm, self).__init__(*args, **kwargs)

        self.fields['exclude_lines'].choices = [(option.pk, '%s: %s' % (option.group.name, option.name)) for option in self.options]

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
            self.attendees = self.attendees.filter(state=AttendState.attended)
        elif attendee_filter == 'not_attended':
            self.attendees = self.attendees.exclude(state=AttendState.attended)
        elif attendee_filter == 'attended_or_paid':
            self.attendees = self.attendees.filter(state=AttendState.attended).filter(paid__gt=0)
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
        excluded_options = self.cleaned_data.get('exclude_lines', [])

        for option in self.options:

            if option.pk in excluded_options:
                continue

            line_groups[option.pk] = self.LineGroup(option.name, option.price)

        pks = [attendee.pk for attendee in self.attendees.all()]

        for selection in Selection.objects.filter(attendee__pk__in=pks).select_related('option', 'attendee'):
            if selection.option.pk in line_groups:
                line_groups[selection.option.pk].add(selection.attendee)

        total = sum_attendee_payment_status(self.attendees)

        return self.attendees, line_groups.values(), total, \
               show_regular_attendees, show_irregular_attendees, attendee_filter_label


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
                       'minimum_selected', 'maximum_selected'),
            S2Fieldset(_('Package'),
                       'package_price'))

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

        if 'instance' in kwargs:
            del self.fields['type']

        self.helper = S2FormHelper(horizontal=True)

        if 'instance' in kwargs:
            type = kwargs['instance'].get_type_display()
            fields = ('name',
                      HTML('<div class="form-group"><label class="control-label col-lg-2">Type:</label><div class="controls col-lg-8">%s</div></div>' % type),
                      'description',
                      'price')
        else:
            fields = ('name', 'type', 'description', 'price')

        layout = S2Layout(
            S2Fieldset(None,
                       *fields))

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


def attendee_selection_helper_factory(option_group, visible_fields):

    layout = S2Layout(
        S2Fieldset(option_group.name, *visible_fields, collapse=False, show_help_text=False)
    )

    helper = S2FormHelper(horizontal=True)
    helper.add_layout(layout)
    helper.form_tag = False

    return helper


class UserForm(forms.ModelForm):
    class Meta:
        model = UserProfile

        widgets = {
            'dateofbirth': SplitDateWidget(),
        }

        exclude = ('date_joined', 'last_login', 'password', 'user')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        self.helper = S2FormHelper(horizontal=True)

        layout = S2Layout(
            S2Fieldset(None,
                       'username'),
            S2Fieldset(_('Personal info'),
                       'first_name', 'last_name', 'sex', 'dateofbirth', collapse=False),
            S2Fieldset(_('Contact'),
                       'email', 'phonenumber', collapse=False),
            S2Fieldset(_('Address'),
                       'street', 'postalcode', 'city', 'country'),
            S2Fieldset(_('Other'),
                       'send_me_email', 'picture'),
            S2Fieldset(_('Access'),
                       'is_active', 'is_staff', 'is_superuser', 'groups'))

        self.helper.add_layout(layout)
        self.helper.add_input(S2SubmitUpdate() if 'instance' in kwargs else S2SubmitCreate())


class PasswordForm(forms.Form):

    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password (again)"),
                                widget=forms.PasswordInput)

    helper = S2FormHelper(horizontal=True)

    layout = S2Layout(
        S2Fieldset(None,
                   'password1', 'password2'))

    helper.add_layout(layout)
    helper.add_input(S2SubmitUpdate())

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')

        super(PasswordForm, self).__init__(*args, **kwargs)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1', None)
        password2 = self.cleaned_data.get('password2', None)

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('The two password fields didn\'t match.'))

        return password2

    def save(self):
        self.instance.set_password(self.cleaned_data['password1'])
        self.instance.save()


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)

        self.helper = S2FormHelper(horizontal=True)

        layout = S2Layout(
            S2Fieldset(None,
                       'name', 'permissions'))

        self.helper.add_layout(layout)
        self.helper.add_input(S2SubmitUpdate() if 'instance' in kwargs else S2SubmitCreate())
