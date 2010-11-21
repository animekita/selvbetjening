from django import forms
from django.utils.translation import ugettext as _

from uni_form.helpers import FormHelper, Submit, Fieldset, Layout

from selvbetjening.data.events.models import AttendState, Attend, Event
from selvbetjening.viewhelpers.forms.helpers import InlineFieldset

class EventForm(forms.ModelForm):
    class Meta:
        model = Event

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)

        layout_fields = [_('Event')] + list(self.fields)
        layout = Layout(InlineFieldset(*layout_fields))

        helper = FormHelper()
        helper.add_layout(layout)
        helper.add_input(Submit('submit_event', _('Save Event')))
        helper.form_tag = True
        helper.use_csrf_protection = True

        self.helper = helper

class AttendeeForm(forms.ModelForm):
    class Meta:
        model = Attend
        fields = ('state',)

    helper = FormHelper()
    helper.add_layout(InlineFieldset(None))
    helper.add_input(Submit('submit_attendee', _('Save State')))
    helper.form_tag = False
    helper.use_csrf_protection = True

class CheckinForm(forms.Form):
    def __init__(self, *args, **kwargs):

        attendee = kwargs.pop('attendee')
        helper = FormHelper()
        helper.add_layout(InlineFieldset(None))
        helper.form_tag = True
        helper.use_csrf_protection = True

        if attendee.state == AttendState.attended:
            checkout = Submit(_('Checkout'), _('Checkout'))
            helper.add_input(checkout)
        else:
            checkin_and_pay = Submit(_('Checkin and Pay'), _('Checkin and Pay'))
            checkin = Submit(_('Checkin only'), _('Checkin only'))
            helper.add_input(checkin_and_pay)
            helper.add_input(checkin)

        self.helper = helper

        super(CheckinForm, self).__init__(*args, **kwargs)