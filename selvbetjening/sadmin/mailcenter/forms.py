from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models import ManyToOneRel
from django.core.urlresolvers import reverse

from selvbetjening.core.events.models import AttendState
from selvbetjening.core.mailcenter.models import UserConditions, \
     AttendConditions, BoundAttendConditions

from selvbetjening.portal.eventregistration.forms import AcceptForm

from selvbetjening.sadmin.base.widgets import SAdminForeignKeyRawIdWidget

class SendEmailForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SendEmailForm, self).__init__(*args, **kwargs)

        self.fields['username'] = forms.CharField(
            widget=SAdminForeignKeyRawIdWidget(ManyToOneRel(User, 'username'),
                                               url=reverse('sadmin:auth_user_changelist')))

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

        instance.save()

        self.save_m2m()

        return instance

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

    attends_state = forms.MultipleChoiceField(choices=AttendState.get_choices(), required=False)

    fieldsets = [(_('Attends'), {
        'fields': ('event',
                   ('attends_selection_comparator', 'attends_selection_argument'),
                   'attends_state'),
        })
    ]

class BoundAttendConditionForm(BaseConditionForm):
    class Meta:
        model = BoundAttendConditions
        exclude = ['specification']

    attends_state = forms.MultipleChoiceField(choices=AttendState.get_choices(), required=False)

    fieldsets = [(_('Event'), {
        'fields': ('event',
                   ('attends_selection_comparator', 'attends_selection_argument'),
                   'attends_state'),
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