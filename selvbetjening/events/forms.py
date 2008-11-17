# coding=UTF-8

from django.utils.translation import ugettext as _, ungettext
from django import forms
from django.contrib.auth.models import User

from selvbetjening.core.forms import AcceptForm

class SignupForm(AcceptForm):

    def label(self):
        return _(u"I have read and accept the above described terms")

    def error(self):
        return _(u"You must accept to participate in the event")

class SignoffForm(AcceptForm):
    def label(self):
        return _(u"Yes, remove me from the event")

    def error(self):
        return _(u"You must accept to remove your participation in the event")

class OptionsForm(forms.Form):

    def __init__(self, user, event, *args, **kwargs):
        self.user = user
        self.event = event

        kwargs['initial'] = {}
        for option in user.option_set.all():
            kwargs['initial'][self._get_id(option)] = True

        super(forms.Form, self).__init__(*args, **kwargs)

        self.Meta.layout = []

        self.optiongroups = self.event.optiongroup_set.all()
        self.options = []

        for optiongroup in self.optiongroups:
            groupoptions = []
            for option in optiongroup.option_set.all().order_by('order'):
                self.options.append(option)
                groupoptions.append((self._get_id(option), {'disabled' : option.is_frozen()}))
                self.fields[self._get_id(option)] = forms.BooleanField(label=option.name,
                                                                       required=False,
                                                                       help_text=option.description)
            self.Meta.layout.append((optiongroup.name, groupoptions, optiongroup.description))

    class Meta:
        pass


    def clean(self):
        for optiongroup in self.optiongroups:
            if optiongroup.minimum_selected > 0:
                selected = 0
                for option in optiongroup.option_set.all():
                    if option.is_frozen():
                        if self.initial.get(self._get_id(option), False):
                            selected += 1

                    elif self.cleaned_data.get(self._get_id(option), False):
                        selected += 1

                if selected < optiongroup.minimum_selected:

                    args = {'count' :optiongroup.minimum_selected,
                            'group' : optiongroup.name
                            }

                    if optiongroup.minimum_selected == 1:
                        error = _('You need to select one option from the group %(group)s') % args
                    else:
                        error = _('You need to select %(count)d options from the group %(group)s') % args

                    raise forms.ValidationError(error)

        return self.cleaned_data

    def save(self):
        if not hasattr(self, 'cleaned_data'):
            return

        for option in self.options:
            if option.is_frozen():
                continue

            if self.cleaned_data.get(self._get_id(option), False):
                # option selected
                if not self.initial.get(self._get_id(option), False):
                    # option where not selected before
                    option.users.add(self.user)
            else:
                # option not selected
                if self.initial.get(self._get_id(option), False):
                    # option where selected before
                    option.users.remove(self.user)

    @staticmethod
    def _get_id(option):
        return 'option_' + str(option.pk)
