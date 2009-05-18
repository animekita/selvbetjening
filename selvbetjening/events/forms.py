# coding=UTF-8

from django.utils.translation import ugettext as _
from django import forms

from selvbetjening.core.forms import AcceptForm

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

class OptionsForm(forms.Form):

    class Meta:
        layout = [] # populated by the constructor

    def __init__(self, user, event, *args, **kwargs):
        self.user = user
        self.event = event
        self.Meta.layout = []

        selected = user.option_set.all()

        kwargs['initial'] = {}
        for option in selected:
            kwargs['initial'][self._get_id(option)] = True

        super(forms.Form, self).__init__(*args, **kwargs)

        self.options = []
        for optiongroup in self.event.optiongroup_set.all():

            user_is_attending_group = self.user in optiongroup.attendees
            disable_group = optiongroup.is_frozen()
            if optiongroup.max_attendees_reached() and not user_is_attending_group:
                disable_all = True

            options = []
            options_layout = []
            for option in optiongroup.option_set.all().order_by('order'):
                user_is_attending = option in selected

                disable = disable_group or option.is_frozen()
                if option.max_attendees_reached() and not user_is_attending:
                    disable = True

                options.append((option, disable, user_is_attending))

                # insert option in form
                options_layout.append((self._get_id(option), {'disabled' : disable}))
                self.fields[self._get_id(option)] = forms.BooleanField(label=option.name,
                                                                       required=False,
                                                                       help_text=option.description)

                # clean function for option
                setattr(self, 'clean_%s' % self._get_id(option), self._clean_option(option, disable, user_is_attending))

            self.Meta.layout.append((optiongroup.name, options_layout, optiongroup.description, optiongroup.id))
            setattr(self, 'clean_%s' % optiongroup.id, self._clean_optiongroup(optiongroup,
                                                                               disable_group,
                                                                               user_is_attending_group,
                                                                               options))

            self.options += options

    def save(self):
        if not hasattr(self, 'cleaned_data'):
            return

        for option_data in self.options:
            option, disable, user_is_attending = option_data

            if option.is_frozen():
                continue

            if self.cleaned_data.get(self._get_id(option), False):
                if not user_is_attending:
                    option.users.add(self.user)
            else:
                if user_is_attending:
                    option.users.remove(self.user)

    def _clean_optiongroup(self, optiongroup, disable_group, user_is_attending_group, options):
        def clean_func():
            selected_options_in_group = 0
            for option_data in options:
                option, disable, user_is_attending = option_data

                if disable and user_is_attending:
                    selected_options_in_group += 1
                elif self.cleaned_data.get(self._get_id(option), False):
                    selected_options_in_group += 1

            if optiongroup.max_attendees_reached() and not user_is_attending_group:
                if selected_options_in_group > 0:
                    raise forms.ValidationError('The maximum number of attendees have been reached')

            if optiongroup.minimum_selected > 0 and \
               optiongroup.minimum_selected > selected_options_in_group:

                args = {'count' :optiongroup.minimum_selected,
                        'group' : optiongroup.name
                        }

                if optiongroup.minimum_selected == 1:
                    error = _('You need to select one option from the group %(group)s') % args
                else:
                    error = _('You need to select %(count)d options from the group %(group)s') % args

                raise forms.ValidationError(error)

            if optiongroup.maximum_selected > 0 and \
               optiongroup.maximum_selected < selected_options_in_group:

                args = {'count' :optiongroup.maximum_selected,
                        'group' : optiongroup.name
                        }

                if optiongroup.minimum_selected == 1:
                    error = _('You can not select more than one option from the group %(group)s') % args
                else:
                    error = _('You can not select more than %(count)d options from the group %(group)s') % args

                raise forms.ValidationError(error)

        return clean_func

    def _clean_option(self, option, disable, user_is_attending):
        def clean_func():
            selected = self.cleaned_data.get(self._get_id(option), False)
            if selected and \
               option.max_attendees_reached() and \
               not user_is_attending:
                raise forms.ValidationError(_('The maximum number of attendees have been reached'))

            return selected

        return clean_func

    @staticmethod
    def _get_id(option):
        return 'option_' + str(option.pk)
