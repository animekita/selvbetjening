
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Row, Fieldset
from crispy_forms.bootstrap import Tab, TabHolder

from selvbetjening.core.events.models import Event


class S2FormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(S2FormHelper, self).__init__(*args, **kwargs)
        self.form_class = 'form-horizontal'
        self.html5_required = True


class S2Field(Field):
    def __init__(self, *args, **kwargs):
        kwargs['css_class'] = 'input-xxlarge'
        super(S2Field, self).__init__(*args, **kwargs)


class EventForm(ModelForm):
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


class EventDisplayForm(ModelForm):
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

