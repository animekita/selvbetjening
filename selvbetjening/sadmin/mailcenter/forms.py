from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from uni_form.helpers import FormHelper, Submit, Fieldset, Layout, Row

from selvbetjening.viewbase.forms.helpers import InlineFieldset
from selvbetjening.core.mailcenter.models import EmailSpecification,\
     UserConditions, AttendConditions, EventConditions
from selvbetjening.portal.eventregistration.forms import AcceptForm
from selvbetjening.core.events.models import Event, Option, AttendState

class SendPreviewEmailForm(forms.Form):
    username = forms.CharField()

    layout = Layout(InlineFieldset(_(u'Send Preview E-mail'), 'username'))
    submit = Submit('submit_send_preview', _(u'Send Preview E-mail'))

    helper = FormHelper()
    helper.add_layout(layout)
    helper.add_input(submit)

    def clean_username(self):
        username = self.cleaned_data['username']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(_(u'User not found'))

        self.cleaned_data['user'] = user
        return username

class SendNewsletterForm(AcceptForm):
    def __init__(self, *args, **kwargs):
        super(SendNewsletterForm, self).__init__(*args, **kwargs)

        layout = Layout(InlineFieldset(_(u'Confirm Send Newsletter'), 'confirm'))
        submit = Submit('submit_confirm_send_newsletter', _(u'Confirm Send Newsletter'))

        self.helper.add_layout(layout)
        self.helper.add_input(submit)

    def label(self):
        return _(u'Yes, send the newsletter to all users.')

    def error(self):
        return _(u'You must confirm you actually want to send this e-mail to all users.')

class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailSpecification
        fields = ('subject', 'body')

    layout = Layout(InlineFieldset(_(u'E-mail Template'), 'subject', 'body'))

    helper = FormHelper()
    helper.add_layout(layout)
    helper.form_tag = False

class EmailSourceForm(forms.ModelForm):
    class Meta:
        model = EmailSpecification
        fields = ('source_enabled', 'event',)

    layout = Layout(InlineFieldset(_(u'Bind to Event'), 'source_enabled', 'event'))

    helper = FormHelper()
    helper.add_layout(layout)
    helper.form_tag = False

class BaseConditionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.specification = kwargs.pop('email_specification')

        try:
            kwargs['instance'] = self.Meta.model.objects.get(specification=self.specification)
        except self.Meta.model.DoesNotExist:
            pass

        super(BaseConditionForm, self).__init__(*args, **kwargs)

    def save(self):
        instance = super(BaseConditionForm, self).save(commit=False)
        instance.specification = self.specification

        return instance.save()

class UserConditionForm(BaseConditionForm):
    class Meta:
        model = UserConditions
        exclude = ['specification',]

    layout = Layout(InlineFieldset(_('User'),
                                   Row('user_age_comparator', 'user_age_argument')))

    helper = FormHelper()
    helper.add_layout(layout)
    helper.form_tag = False

class AttendeeConditionForm(BaseConditionForm):
    class Meta:
        model = AttendConditions
        exclude = ['specification',]

    attends_status = forms.MultipleChoiceField(choices=AttendState.get_choices(), required=False)

    layout = Layout(InlineFieldset(_('Attends'), 'attends_event',
                                   Row('attends_selection_comparator', 'attends_selection_argument'),
                                   'attends_status'))

    helper = FormHelper()
    helper.add_layout(layout)
    helper.form_tag = False

class EventConditionForm(BaseConditionForm):
    class Meta:
        model = EventConditions
        exclude = ['specification']

    attends_status = forms.MultipleChoiceField(choices=AttendState.get_choices(), required=False)

    layout = Layout(InlineFieldset(_('Event'),
                                   Row('attends_selection_comparator',
                                       'attends_selection_argument'),
                                   'attends_status'))

    helper = FormHelper()
    helper.add_layout(layout)
    helper.form_tag = False

class ConditionFormRegistry(object):
    def __init__(self):
        self._condition_forms = {}

    def register(self, condition, form):
        self._condition_forms[condition] = form

    def get_forms(self, keys):
        return [self._condition_forms[key.__class__] for key in keys]

conditionform_registry = ConditionFormRegistry()

conditionform_registry.register(UserConditions, UserConditionForm)
conditionform_registry.register(AttendConditions, AttendeeConditionForm)
conditionform_registry.register(EventConditions, EventConditionForm)