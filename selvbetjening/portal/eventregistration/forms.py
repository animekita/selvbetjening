# coding=UTF-8

from django.utils.translation import ugettext as _
from django.utils.translation import ungettext_lazy, ugettext_lazy
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Fieldset, Layout

from selvbetjening.core.events.forms import OptionForms as BaseOptionForms
from selvbetjening.core.events.forms import OptionGroupForm as BaseOptionGroupForm

class AcceptForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AcceptForm, self).__init__(*args, **kwargs)

        self.fields['confirm'] = forms.BooleanField(widget=forms.CheckboxInput(),
                                                    label=self.label())

        self.helper = FormHelper()
        self.helper.add_layout(Layout(Fieldset(self.heading(), 'confirm')))

    def heading(self):
        return None

    def label(self):
        return u'Accept'

    def error(self):
        return u'Error'

    def clean_confirm(self):
        if self.cleaned_data.get('confirm', False):
            return self.cleaned_data['confirm']
        raise forms.ValidationError(self.error())

    def save(self):
        pass

class SignupForm(AcceptForm):
    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)

        layout = Layout(Fieldset(ugettext_lazy(u"Accept terms"),
                                       'confirm'))
        self.helper.add_layout(layout)
        self.helper.form_tag = False

    def label(self):
        return _(u'I have read and accept the above described terms')

    def error(self):
        return _(u'You must accept to participate in the event')

class SignoffForm(AcceptForm):
    def __init__(self, *args, **kwargs):
        super(SignoffForm, self).__init__(*args, **kwargs)

        layout = Layout(Fieldset('', 'confirm'))

        submit = Submit(_('Sign off'), _('Sign off'))
        self.helper.add_input(submit)
        self.helper.add_layout(layout)

    def label(self):
        return _(u'Yes, remove me from the event')

    def error(self):
        return _(u'You must accept to remove your participation in the event')

class OptionGroupForm(BaseOptionGroupForm):

    def _should_save(self, option, suboptions, disabled):
        return disabled == False

    def _display_option(self, option, disabled, suboptions, display_params=None):
        if display_params is None:
            display_params = {}

        if disabled:
            display_params['disabled'] = 'disabled'

        return super(OptionGroupForm, self)._display_option(option, disabled, suboptions, display_params)

    def _register_clean_function(self, option, selected_initially, disabled):
        def clean_disabled_option():
            selected = self.cleaned_data.get(self._get_id(option), False)

            if selected_initially:
                self.selected_total += 1
                return

            if selected and option.max_attendees_reached():
                raise forms.ValidationError(_('The maximum number of attendees have been reached'))

            if selected and option.is_frozen():
                raise forms.ValidationError(_('This option can not be selected anymore'))

        def clean_enabled_option():
            selected = self.cleaned_data.get(self._get_id(option), False)

            if selected:
                self.selected_total += 1

            return selected

        if disabled:
            clean_option = clean_disabled_option
        else:
            clean_option = clean_enabled_option

        setattr(self, 'clean_%s' % self._get_id(option), clean_option)

    def clean(self):
        if self.optiongroup.minimum_selected > 0 and \
           self.optiongroup.minimum_selected > self.selected_total:

            error = ungettext_lazy('You need to select one option from the group %(group)s',
                              'You need to select %(count)d options from the group %(group)s',
                              self.optiongroup.minimum_selected) % {
                                  'count' : self.optiongroup.minimum_selected,
                                  'group' : self.optiongroup.name
                              }

            raise forms.ValidationError(error)

        if self.optiongroup.maximum_selected > 0 and \
           self.optiongroup.maximum_selected < self.selected_total:

            error = ungettext_lazy('You can not select more than one option from the group %(group)s',
                              'You can not select more than %(count)d options from the group %(group)s',
                              self.optiongroup.maximum_selected) % {
                                  'count' : self.optiongroup.maximum_selected,
                                  'group' : self.optiongroup.name
                              }

            raise forms.ValidationError(error)

        return self.cleaned_data

class OptionForms(BaseOptionForms):
    optiongroupform = OptionGroupForm