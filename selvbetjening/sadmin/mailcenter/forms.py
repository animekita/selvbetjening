from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from uni_form.helpers import FormHelper, Submit, Fieldset, Layout, Row

from selvbetjening.viewhelpers.forms.helpers import InlineFieldset
from selvbetjening.clients.mailcenter.models import EmailSpecification, Condition
from selvbetjening.clients.eventregistration.forms import AcceptForm

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

class ConditionForm(forms.ModelForm):
    class Meta:
        model = Condition
        fields = ('negate_condition', 'field', 'comparator', 'argument')

    negate_condition = forms.BooleanField(label=_(u'Negate'), required=False)
    field = forms.ChoiceField()
    comparator = forms.ChoiceField()
    argument = forms.CharField()

    layout = Layout(InlineFieldset(_('Condition'),
                                   Row('negate_condition', 'field', 'comparator', 'argument')))

    helper = FormHelper()
    helper.add_layout(layout)
    helper.form_tag = False

    def __init__(self, *args, **kwargs):
        specification = kwargs.pop('email_specification')

        super(ConditionForm, self).__init__(*args, **kwargs)

        try:
            self.instance.specification
        except EmailSpecification.DoesNotExist:
            self.instance.specification = specification

        self.fields['field'].choices = self.instance.field_choices
