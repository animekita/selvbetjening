
from decimal import Decimal
from collections import OrderedDict

from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms.formsets import formset_factory, BaseFormSet
from django.forms.util import ErrorList
from django.template.defaultfilters import floatformat
from django.utils.translation import ugettext as _

from selvbetjening.core.events.options.dynamic_selections import dynamic_options, SCOPE
from selvbetjening.core.events.models import Selection, Attend, SubOption
from selvbetjening.core.events.utils import sum_attendee_payment_status
from selvbetjening.core.events.signals import find_attendee_signal
from selvbetjening.core.events.models import Event, AttendState, OptionGroup, Option, \
    AttendeeComment, Payment

from selvbetjening.core.mailcenter.models import EmailSpecification

from selvbetjening.frontend.utilities.forms import *


class EventForm(forms.ModelForm):
    class Meta:
        model = Event

        widgets = {
            'tagline': forms.Textarea(attrs={'rows': 2}),
            'description': forms.Textarea(attrs={'rows': 2}),
            'startdate': SplitDateWidget(),
            'enddate': SplitDateWidget()
        }

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)

        self.helper = S2FormHelper(horizontal=True)

        layout = S2Layout(
            S2Fieldset(None,
                       'title', 'tagline', 'description', 'group',
                       'startdate', 'enddate',
                       'location', 'location_link',
                       'maximum_attendees',
                       'registration_open'),
            S2Fieldset(_('Conditions'),
                       'move_to_accepted_policy'),
            S2Fieldset(_('Feedback'),
                       'show_custom_signup_message', 'custom_signup_message',
                       'show_custom_change_message', 'custom_change_message',
                       'show_custom_status_page', 'custom_status_page'),
            S2Fieldset(_('Notifications'),
                       'notify_on_registration',
                       'notify_on_registration_update',
                       'notify_on_payment'))

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
            self.attendees = self.attendees.filter(Q(state=AttendState.attended) | Q(paid__gt=0))
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

            for suboption in option.suboptions:
                line_groups['%s-%s' % (option.pk, suboption.pk)] = self.LineGroup('%s (%s)' % (
                    option.name,
                    suboption.name
                ), option.price + suboption.price if suboption.price is not None else 0)

        pks = [attendee.pk for attendee in self.attendees.all()]

        for selection in Selection.objects.filter(attendee__pk__in=pks).select_related('option', 'attendee'):
            if selection.option.pk in line_groups:

                if selection.suboption is None:
                    line_groups[selection.option.pk].add(selection.attendee)

                else:
                    line_groups['%s-%s' % (selection.option.pk, selection.suboption.pk)].add(selection.attendee)

        total = sum_attendee_payment_status(self.attendees)

        return self.attendees, line_groups.values(), total, \
               show_regular_attendees, show_irregular_attendees, attendee_filter_label


class RegisterPaymentForm(forms.Form):
    payment_key = forms.CharField(max_length=255, required=False)
    payment = forms.DecimalField(decimal_places=2, required=False)

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

    def clean(self):

        if 'attendee' not in self.cleaned_data:
            return

        payment = self.cleaned_data.get('payment', None)

        if payment is None or payment == 0:

            if 'payment' not in self._errors:
                self._errors['payment'] = ErrorList()

            self._errors['payment'] = self.error_class([_('Payment field empty')])

            del self.cleaned_data['payment']
            del self.cleaned_data['attendee']
            del self.cleaned_data['handler']
            del self.cleaned_data['payment_key']

        return self.cleaned_data


class BaseRegisterPaymentFormSet(BaseFormSet):

    helper = S2FormHelper(horizontal=False)

    layout = S2Layout(S2Fieldset(
        None,
        S2HorizontalRow(S2Field('payment_key', width=6), S2Field('payment', width=6))
    ))

    submit = Submit('update', _('Register'))

    helper.add_layout(layout)
    helper.add_input(submit)

RegisterPaymentFormSet = formset_factory(RegisterPaymentForm, formset=BaseRegisterPaymentFormSet, extra=8)


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


class SelectOptionType(forms.Form):

    type = forms.ChoiceField(required=True, choices=Option.TYPE_CHOICES)

    helper = S2FormHelper(horizontal=True)

    layout = S2Layout(
        S2Fieldset(None,
                   'type'))

    helper.add_layout(layout)
    helper.add_input(S2SubmitCreate())


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
        model = SUser

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

    def save(self, commit=True):
        self.instance.set_password(self.cleaned_data['password1'])

        if commit:
            self.instance.save()

        return self.instance


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


class TemplateForm(forms.ModelForm):
    class Meta:
        model = EmailSpecification
        fields = ('subject', 'body', 'body_format', 'template_context')

    def __init__(self, *args, **kwargs):
        super(TemplateForm, self).__init__(*args, **kwargs)

        self.helper = S2FormHelper(horizontal=True)

        # TODO add help text on possible params

        layout = S2Layout(
            S2Fieldset(None,
                       'template_context',
                       'subject',
                       'body_format', 'body'))

        self.helper.add_layout(layout)
        self.helper.add_input(S2SubmitUpdate() if 'instance' in kwargs else S2SubmitCreate())


class UserSelectorForm(forms.Form):

    user_selector = forms.CharField(label=_('User Selector'))

    helper = S2FormHelper(horizontal=False)

    layout = S2Layout(
        S2Fieldset(None,
                   S2Field('user_selector', css_class='userselector', autocomplete="off")))

    helper.add_layout(layout)
    helper.add_input(S2Submit('select', _('Select')))

    def clean_user_selector(self):

        data = self.cleaned_data.get('user_selector', '')
        fragments = data.split('-')

        if len(fragments) == 0:
            return forms.ValidationError('Invalid user')

        try:
            user = SUser.objects.get(username=fragments[0].strip())
        except SUser.DoesNotExist:
            raise forms.ValidationError('Invalid user')

        return user

    def get_instance(self):
        return self.cleaned_data['user_selector']


class AttendeeSelectorForm(forms.Form):

    attendee_selector = forms.CharField(label=_('Attendee Selector'))

    helper = S2FormHelper(horizontal=False)

    layout = S2Layout(
        S2Fieldset(None,
                   S2Field('attendee_selector', css_class='attendeeselector', autocomplete="off")))

    helper.add_layout(layout)
    helper.add_input(S2Submit('select', _('Select')))

    def clean_attendee_selector(self):

        data = self.cleaned_data.get('attendee_selector', '')
        fragments = data.split('-')

        if len(fragments) < 2:
            return forms.ValidationError('Invalid attendee')

        event_title = fragments[0].strip()
        username = fragments[1].strip()

        try:
            attendee = Attend.objects.get(event__title=event_title, user__username=username)
        except Attend.DoesNotExist:
            raise forms.ValidationError('Invalid attendee')

        return attendee

    def get_instance(self):
        return self.cleaned_data['attendee_selector']


class AttendeesNewsletterFilter(forms.Form):
    STATUS_CHOICE = AttendState.get_choices()

    status = forms.MultipleChoiceField(
        label=_(u'Attendance status'),
        choices=STATUS_CHOICE,
        help_text=_(u'Only send to recipients with this status. Leave blank to skip this filter.'),
        required=False)

    options = forms.MultipleChoiceField(
        label=_(u'Option selections'),
        help_text=_(u'Only send to recipients who have selected one or more of these options. Leave blank to skip this filter.'),
        required=False)

    def __init__(self, *args, **kwargs):
        event = kwargs.pop('event')
        super(AttendeesNewsletterFilter, self).__init__(*args, **kwargs)

        groups = dynamic_options(SCOPE.SADMIN, event, as_group_dict=True)
        choices = []

        for group_pk, options in groups.items():

            group_choices = []

            for option, selection in options:
                group_choices.append((option.pk, option.name))

            choices.append((options[0][0].group.name, group_choices))

        self.fields['options'].choices = choices

    helper = S2FormHelper(horizontal=False)

    layout = S2Layout(
        S2Fieldset(None,
                   'status', 'options'))

    helper.add_layout(layout)
    helper.add_input(S2Submit('filter', _('Filter')))
    helper.form_tag = False


class AttendeesNewsletterFilterHidden(AttendeesNewsletterFilter):

    def __init__(self, *args, **kwargs):
        super(AttendeesNewsletterFilterHidden, self).__init__(*args, **kwargs)

        self.fields['status'].widget = forms.MultipleHiddenInput()
        self.fields['options'].widget = forms.MultipleHiddenInput()


class SelectionTransferForm(forms.Form):
    STATUS_CHOICE = AttendState.get_choices()

    status = forms.MultipleChoiceField(
        label=_(u'Attendance status'),
        choices=STATUS_CHOICE,
        help_text=_(u'Only transfer attendees with this state. If blank then all attendees will be transferred regardless of their state.'),
        required=False)

    from_option = forms.ChoiceField(
        label=_(u'From option'),
        required=True)

    to_option = forms.ChoiceField(
        label=_(u'To option'),
        required=True)

    email = forms.ModelChoiceField(
        EmailSpecification.objects.all(),
        label=_(u'Notification e-mail to all attendees'),
        required=False
    )

    def __init__(self, *args, **kwargs):
        event = kwargs.pop('event')
        super(SelectionTransferForm, self).__init__(*args, **kwargs)

        choices = []

        for option in Option.objects.filter(group__event=event):

            choices.append((option.pk, '%s - %s,-' % (option.name, floatformat(option.price, "-2"))))

            for suboption in option.suboption_set.all():

                price = 0

                if option.price is not None:
                    price += option.price

                if suboption.price is not None:
                    price += suboption.price

                if price > 0:
                    price_str = ' - %s,-' % floatformat(price, "-2")
                else:
                    price_str = ''

                choices.append((
                    '%s-%s' % (option.pk, suboption.pk),
                    '%s (%s)%s' % (option.name, suboption.name, price_str))
                )

        self.fields['from_option'].choices = choices
        self.fields['to_option'].choices = choices

        self.helper = S2FormHelper(horizontal=False)

        layout = S2Layout(
            S2Fieldset(None,
                'status', 'from_option', 'to_option', 'email'))

        self.helper.add_layout(layout)
        self.helper.add_input(S2Submit('transfer', _('Transfer')))

    def clean_to_option(self):
        pk = self.cleaned_data.get('to_option', None)

        if pk is None:
            raise ValidationError('Invalid choice selected')
        elif '-' in pk:
            option_pk, suboption_pk = pk.split('-')
            self.cleaned_data['to_suboption'] = SubOption.objects.get(pk=suboption_pk)
            return Option.objects.get(pk=option_pk)
        else:
            self.cleaned_data['to_suboption'] = None
            return Option.objects.get(pk=pk)

    def clean_from_option(self):
        pk = self.cleaned_data.get('from_option', None)

        if pk is None:
            raise ValidationError('Invalid choice selected')
        elif '-' in pk:
            option_pk, suboption_pk = pk.split('-')
            self.cleaned_data['from_suboption'] = SubOption.objects.get(pk=suboption_pk)
            return Option.objects.get(pk=option_pk)
        else:
            self.cleaned_data['from_suboption'] = None
            return Option.objects.get(pk=pk)


class SelectionTransferVerificationForm(SelectionTransferForm):

    def __init__(self, *args, **kwargs):
        super(SelectionTransferVerificationForm, self).__init__(*args, **kwargs)

        self.fields['status'].widget = forms.MultipleHiddenInput()
        self.fields['from_option'].widget = forms.HiddenInput()
        self.fields['to_option'].widget = forms.HiddenInput()
        self.fields['email'].widget = forms.HiddenInput()

        self.helper.inputs.pop()