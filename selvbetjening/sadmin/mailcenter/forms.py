from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from uni_form.helpers import FormHelper, Submit, Fieldset, Layout, Row

from selvbetjening.viewbase.forms.helpers import InlineFieldset
from selvbetjening.core.mailcenter.models import EmailSpecification,\
     UserConditions, AttendConditions, BoundAttendConditions
from selvbetjening.portal.eventregistration.forms import AcceptForm
from selvbetjening.core.events.models import Event, Option, AttendState, Attend

class SendEmailForm(forms.Form):
    username = forms.CharField()

    fieldsets = [(None, {
        'fields': ('username',)
        }),
    ]

    def clean_username(self):
        username = self.cleaned_data['username']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(_(u'User not found'))

        self.cleaned_data['user'] = user
        return username

class SendNewsletterForm(AcceptForm):
    fieldsets = [(None, {
        'fields': ('confirm',)
        }),
    ]

    def label(self):
        return _(u'Yes, send the newsletter to all users.')

    def error(self):
        return _(u'You must confirm you actually want to send this e-mail to all users.')

class CreateEmailForm(forms.ModelForm):
    class Meta:
        model = EmailSpecification
        fields = ('subject',)

    layout = Layout(InlineFieldset(None, 'subject',))

    helper = FormHelper()
    helper.add_layout(layout)
    helper.form_tag = False

class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailSpecification
        fields = ('subject', 'body')

    def __init__(self, *args, **kwargs):
        super(EmailTemplateForm, self).__init__(*args, **kwargs)

        help_text = unicode(_(u'Accepts HTML formatted text. E-mails are sent in both HTML and plain text formats. Furthermore, the following variables are made available')) + '<br/>'
        help_text_user = '<br/>user.(username|first_name|last_name|email|get_age)'
        help_text_attendee = '<br/>attendee.event(title)'

        instance = kwargs.pop('instance', None)
        if instance is not None:
            for parameter in instance.required_parameters:
                if parameter is User:
                    help_text += help_text_user
                if parameter is Attend:
                    help_text += help_text_attendee

        self.fields['body'].help_text = help_text

    layout = Layout(InlineFieldset(None, 'subject', 'body'))

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

    fieldsets = [(_('User'), {
        'fields': (('user_age_comparator', 'user_age_argument'),),
        }),
    ]

class AttendeeConditionForm(BaseConditionForm):
    class Meta:
        model = AttendConditions
        exclude = ['specification',]

    attends_status = forms.MultipleChoiceField(choices=AttendState.get_choices(), required=False)

    fieldsets = [(_('Attends'), {
        'fields': ('event', 
                   ('attends_selection_comparator', 'attends_selection_argument'),
                   'attends_status'),
        })
    ]

class BoundAttendConditionForm(BaseConditionForm):
    class Meta:
        model = BoundAttendConditions
        exclude = ['specification']

    attends_status = forms.MultipleChoiceField(choices=AttendState.get_choices(), required=False)

    fieldsets = [(_('Event'), {
        'fields': ('event', 
                   ('attends_selection_comparator', 'attends_selection_argument'),
                   'attends_status'),
        })
    ]
    
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
conditionform_registry.register(BoundAttendConditions, BoundAttendConditionForm)