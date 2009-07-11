# coding=UTF-8

from django.utils.translation import ugettext as _
from django.utils.translation import ungettext_lazy
from django import forms

class DummyWidget(forms.Widget):
    def render(self):
        return forms.mark_safe(u'')

class AcceptForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(AcceptForm, self).__init__(*args, **kwargs)

        self.fields['confirm'] = forms.BooleanField(widget=forms.CheckboxInput(),
                             label=self.label())

    def clean_confirm(self):
        if self.cleaned_data.get('confirm', False):
            return self.cleaned_data['confirm']
        raise forms.ValidationError(self.error())

    def save(self):
        pass
    
class SignupForm(AcceptForm):

    def label(self):
        return _(u'I have read and accept the above described terms')

    def error(self):
        return _(u'You must accept to participate in the event')

class SignoffForm(AcceptForm):
    def label(self):
        return _(u'Yes, remove me from the event')

    def error(self):
        return _(u'You must accept to remove your participation in the event')

class OptionForms(object):
    def __init__(self, event, post=None, selected_options=None):
        self.forms = []
        
        if selected_options is None:
            selected_options = []

        for optiongroup in event.optiongroup_set.all():
            if post is None:
                self.forms.append(OptionGroupForm(optiongroup, 
                                                  selected_options=selected_options))
            else:
                self.forms.append(OptionGroupForm(optiongroup, post, selected_options=selected_options))

    def is_valid(self):
        is_valid = True
        for form in self.forms:
            is_valid = is_valid and form.is_valid()

        return is_valid

    def save_selection(self, attendee):
        for form in self.forms:
            form.save_selection(attendee)

    def __iter__(self):
        for form in self.forms:
            yield form

class OptionGroupForm(forms.Form):

    def __init__(self, optiongroup, *args,  **kwargs):
        self.optiongroup = optiongroup
        self.selected_total = 0
        self.selected_initally = False
        self.enabled_options = []
        
        if kwargs.has_key('selected_options'):
            
            selected_options = [option for option in kwargs.pop('selected_options') if option.group == optiongroup]
        else:
            selected_options = []

        class Meta:
            layout = [[optiongroup.name,
                       [],
                       optiongroup.description,
                       optiongroup.id],]

        self.Meta = Meta

        kwargs['initial'] = {}
        for option in selected_options:
            kwargs['initial'][self._get_id(option)] = True

        super(OptionGroupForm, self).__init__(*args, **kwargs)

        for option in optiongroup.option_set.all().order_by('order'):
            selected = option in selected_options

            disabled = option.max_attendees_reached() and not selected
            disabled = disabled or option.is_frozen()

            self._display_option(option, disabled)

            if not disabled:
                self.enabled_options.append(option)
                
            self._register_clean_function(option, selected, disabled)

    def _display_option(self, option, disabled):
        self.Meta.layout[0][1].append((self._get_id(option), {'disabled' : disabled}))
        self.fields[self._get_id(option)] = forms.BooleanField(label=option.name,
                                                               required=False,
                                                               help_text=option.description)

    def _register_clean_function(self, option, selected_initially, disabled):
        def clean_disabled_option():
            selected = self.cleaned_data.get(self._get_id(option), False)
            
            if selected_initially:
                self.selected_total += 1
                
            if selected and \
               option.max_attendees_reached() and \
               not selected_initially:
                raise forms.ValidationError(_('The maximum number of attendees have been reached'))

            if selected and \
               option.is_frozen():
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

    def save_selection(self, attendee):
        for option in self.enabled_options:
            if self.cleaned_data.get(self._get_id(option), False):
                attendee.select_option(option)
            else:
                attendee.deselect_option(option)

    @staticmethod
    def _get_id(option):
        return 'option_' + str(option.pk)
