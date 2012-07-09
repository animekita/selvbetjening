from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm

from crispy_forms.helpers import FormHelper, Submit, Fieldset, Layout

from selvbetjening.viewbase.forms.helpers import Fieldset

from selvbetjening.core.translation.utility import translate_model
from selvbetjening.core.invoice.models import Payment

from models import AttendState

class OptionGroupForm(forms.Form):
    def __init__(self, optiongroup, *args,  **kwargs):
        self.optiongroup = translate_model(optiongroup)
        self.selected_total = 0
        self.selected_initally = False
        self.save_options = []
        self.attendee = kwargs.pop('attendee', None)

        if self.attendee is not None:
            selections = [selection for selection in self.attendee.selections if selection.option.group == optiongroup]
        else:
            selections = []

        kwargs['initial'] = {}
        for selection in selections:
            kwargs['initial'][self._get_id(selection.option)] = True
            if selection.suboption:
                kwargs['initial'][self._get_sub_id(selection.option)] = selection.suboption.id

        super(OptionGroupForm, self).__init__(*args, **kwargs)

        self.selected_option_pks = [selection.option.pk for selection in selections]

        display_params = None

        # package controls
        if optiongroup.package_solution:
            self.fields[self._get_package_id(optiongroup)] = \
                forms.BooleanField(label=_(u'Package'), required=False,
                                   widget=forms.CheckboxInput(attrs={'class': 'package'}))

            display_params = {'class': 'in_package in_package_%s' % optiongroup.pk}

        for option in optiongroup.options:
            translate_model(option)

            selected = option.pk in self.selected_option_pks

            disabled = self.attendee is not None and \
                self.optiongroup.lock_selections_on_acceptance == True and \
                self.attendee.state != AttendState.waiting
            disabled = disabled or (option.max_attendees_reached() and not selected)
            disabled = disabled or option.is_frozen()

            suboptions = option.suboptions

            if self._should_save(option, suboptions, disabled):
                self.save_options.append((option, suboptions))

            self._display_option(option, disabled, suboptions, display_params=display_params)
            self._register_clean_function(option, selected, disabled)

        # setup display related settings

        fields = [self.optiongroup.name,] + [field_id for field_id in self.fields]
        options = {'help_text' : self.optiongroup.description,
                   'large_hints' : True}

        layout = Layout(Fieldset(*fields, **options))

        self.helper = FormHelper()

        self.helper.add_layout(layout)
        self.helper.form_tag = False
        self.helper.use_csrf_protection = True

    def _should_save(self, option, suboptions, disabled):
        return True

    def _display_option(self, option, disabled, suboptions, display_params=None):
        if display_params is None:
            display_params = {}

        #if len(suboptions) > 0:
        #    display_params['children'] = (self._get_sub_id(option),)

        if option.price == 0:
            label = option.name
        else:
            label = '%s (%s,-)' % (option.name, option.price)

        self.fields[self._get_id(option)] = forms.BooleanField(label=label,
                                                               required=False,
                                                               help_text=option.description,
                                                               widget=forms.CheckboxInput(attrs=display_params))

        if len(suboptions) > 0:
            choices = [(suboption.id, suboption.name) for suboption in suboptions]
            self.fields[self._get_sub_id(option)] = forms.ChoiceField(label=_('Choices'),
                                                                      choices=choices,
                                                                      required=False)

    def _register_clean_function(self, option, selected_initially, disabled):
        pass

    def clean(self):
        return self.cleaned_data

    def save(self, attendee=None):
        if self.attendee is None:
            self.attendee = attendee

        for option, suboptions in self.save_options:
            if self.cleaned_data.get(self._get_id_pk(option.pk), False):
                suboption_id = self.cleaned_data.get(self._get_sub_id(option), None)

                if suboption_id:
                    suboption = suboptions.get(pk=suboption_id)
                else:
                    suboption = None

                self.attendee.select_option(option, suboption)
            else:
                self.attendee.deselect_option(option)

    def is_selected(self, option_pk):
        if option_pk in [option.pk for option, suboptions in self.save_options]:
            return self.cleaned_data.get(self._get_id_pk(option_pk), False)
        else:
            return option_pk in self.selected_option_pks

    @staticmethod
    def _get_id_pk(option_pk):
        return 'option_' + str(option_pk)

    @staticmethod
    def _get_id(option):
        return 'option_' + str(option.pk)

    @staticmethod
    def _get_sub_id(option):
        return 'suboptions_' + str(option.pk)

    @staticmethod
    def _get_package_id(optiongroup):
        return 'package_' + str(optiongroup.pk)

class OptionForms(object):
    optiongroupform = OptionGroupForm

    def __init__(self, event, post=None, attendee=None):
        self.forms = []

        for optiongroup in event.optiongroups.order_by('order'):
            if post is None:
                self.forms.append(self.optiongroupform(optiongroup,
                                                       attendee=attendee))
            else:
                self.forms.append(self.optiongroupform(optiongroup,
                                                       post,
                                                       attendee=attendee))

    def is_valid(self):
        is_valid = True
        for form in self.forms:
            is_valid = is_valid and form.is_valid()

        return is_valid

    def save(self, attendee=None):
        for form in self.forms:
            form.save(attendee=attendee)

    def is_selected(self, option_pk):
        for form in self.forms:
            if form.is_selected(option_pk):
                return True

        return False

    def __iter__(self):
        for form in self.forms:
            yield form

class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = ('amount', 'note')

    layout = Layout(Fieldset(_(u'Payment'), *Meta.fields))
    submit = Submit('submit_payment', _('Pay'))

    helper = FormHelper()

    helper.add_layout(layout)
    helper.add_input(submit)
    helper.form_tag = True
    helper.use_csrf_protection = True