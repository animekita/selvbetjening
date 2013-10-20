
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from core.events.models.options import AutoSelectChoiceOption

from selvbetjening.core.events.options.scope import SCOPE
from selvbetjening.core.events.models import Selection, Option


class BaseTypeManager(object):

    @staticmethod
    def get_model():
        return Option

    @staticmethod
    def get_model_fields():
        return 'name', 'description', 'price', 'auto_select_suboption'


class BooleanWidget(object):

    def __init__(self, option):
        self.option = option

    def get_field(self):

        return forms.BooleanField(
            label=self.option.name,
            required=False,
            help_text=self.option.description,
            widget=forms.CheckboxInput())

    def save_callback(self, attendee, value):

        if value is not None and value:
            Selection.objects.get_or_create(
                option_id=self.option.pk,
                attendee=attendee
            )
        else:
            Selection.objects.filter(
                option_id=self.option.pk,
                attendee=attendee
            ).delete()

    def clean_callback(self, value):
        return value if value is not None else False

    def initial_value(self, selection):
        return True


class BooleanTypeManager(BaseTypeManager):

    @staticmethod
    def get_widget(scope, option):
        return BooleanWidget(option)


class TextWidget(object):

    def __init__(self, option):
        self.option = option

    def get_field(self):

        return forms.CharField(
            label=self.option.name,
            required=False,
            help_text=self.option.description,
            widget=forms.TextInput())

    def save_callback(self, attendee, value):

        if value is not None and len(value.strip()) > 0:
            selection, created = Selection.objects.get_or_create(
                option_id=self.option.pk,
                attendee=attendee
            )

            selection.text = value.strip()
            selection.save()
        else:
            Selection.objects.filter(
                option_id=self.option.pk,
                attendee=attendee
            ).delete()

    def clean_callback(self, value):
        return value

    def initial_value(self, selection):
        return selection.text


class TextTypeManager(BaseTypeManager):

    @staticmethod
    def get_widget(scope, option):
        return TextWidget(option)


class ChoiceWidget(object):

    def __init__(self, option):
        self.option = option

        self.choices = [('', '')] + [('suboption_%s' % suboption.pk, suboption.name)
                                     for suboption in self.option.suboptions.all()]

    def get_field(self):

        return forms.ChoiceField(
            label=self.option.name,
            required=False,
            help_text=self.option.description,
            widget=forms.Select(),
            choices=self.choices)

    def save_callback(self, attendee, value):

        if value is not None and len(value) > 0:
            selection, created = Selection.objects.get_or_create(
                option_id=self.option.pk,
                attendee=attendee
            )

            _, pk = value.split('_')

            selection.suboption_id = pk
            selection.save()

        else:
            Selection.objects.filter(
                option_id=self.option.pk,
                attendee=attendee
            ).delete()

    def clean_callback(self, value):

        if value is None:
            return None

        for choice in self.choices:
            if value == choice[0]:
                return value

        raise ValidationError(_('Choice %s is not allowed') % value)

    def initial_value(self, selection):
        if selection.suboption is not None:
            return 'suboption_%s' % selection.suboption.pk
        else:
            return None


class ChoiceTypeManager(BaseTypeManager):

    @staticmethod
    def get_widget(scope, option):
        return ChoiceWidget(option)


class AutoSelectBooleanWidget(BooleanWidget):

    def get_field(self):
        return forms.BooleanField(
            required=False,
            widget=forms.HiddenInput())

    def clean_callback(self, value):
        return True

    def initial_value(self, selection):
        return True


class AutoSelectTypeManager(BooleanTypeManager):

    @staticmethod
    def get_widget(scope, option):
        if scope == SCOPE.SADMIN:
            return BooleanWidget(option)
        else:
            return AutoSelectBooleanWidget(option)


class AutoSelectChoiceTypeManager(BooleanTypeManager):

    @staticmethod
    def get_model():
        return AutoSelectChoiceOption

    @staticmethod
    def get_model_fields():
        return 'name', 'price', 'auto_select_suboption'

    @staticmethod
    def get_widget(scope, option):
        if scope == SCOPE.SADMIN:
            return ChoiceWidget(option)
        else:
            return AutoSelectBooleanWidget(option)


_type_manager_register = {
    'boolean': BooleanTypeManager,
    'text': TextTypeManager,
    'choices': ChoiceTypeManager,
    'autoselect': AutoSelectTypeManager,
    'autoselectchoice': AutoSelectChoiceTypeManager
}


def type_manager_factory(option_or_type):
    """
    Returns a type manager based on the options type
    """

    return _type_manager_register[option_or_type.type if hasattr(option_or_type, 'type') else option_or_type]