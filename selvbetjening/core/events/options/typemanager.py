
from selvbetjening.core.events.models.options import AutoSelectChoiceOption, DiscountOption
from selvbetjening.core.events.options.widgets import BooleanWidget, TextWidget, ChoiceWidget, AutoSelectBooleanWidget, AutoSelectChoiceWidget, DiscountWidget
from selvbetjening.core.events.options.scope import SCOPE
from selvbetjening.core.events.models import Option


class BaseTypeManager(object):

    @staticmethod
    def get_model():
        return Option


class BooleanTypeManager(BaseTypeManager):

    @staticmethod
    def get_widget(scope, option):
        return BooleanWidget(scope, option)


class TextTypeManager(BaseTypeManager):

    @staticmethod
    def get_widget(scope, option):
        return TextWidget(scope, option)


class ChoiceTypeManager(BaseTypeManager):

    @staticmethod
    def get_widget(scope, option):
        return ChoiceWidget(scope, option)


class AutoSelectTypeManager(BooleanTypeManager):

    @staticmethod
    def get_widget(scope, option):
        if scope == SCOPE.SADMIN:
            return BooleanWidget(scope, option)
        else:
            return AutoSelectBooleanWidget(scope, option)


class AutoSelectChoiceTypeManager(ChoiceTypeManager):

    @staticmethod
    def get_model():
        return AutoSelectChoiceOption

    @staticmethod
    def get_widget(scope, option):
        if scope == SCOPE.SADMIN:
            return ChoiceWidget(scope, option)
        else:
            return AutoSelectChoiceWidget(scope, option)


class DiscountTypeManager(ChoiceTypeManager):

    @staticmethod
    def get_model():
        return DiscountOption

    @staticmethod
    def get_widget(scope, option):
        if scope == SCOPE.SADMIN:
            if option.suboptions.count() > 0:
                return ChoiceWidget(scope, option)
            else:
                return BooleanWidget(scope, option)
        else:
            return DiscountWidget(scope, option)

_type_manager_register = {
    'boolean': BooleanTypeManager,
    'text': TextTypeManager,
    'choices': ChoiceTypeManager,
    'autoselect': AutoSelectTypeManager,
    'autoselectchoice': AutoSelectChoiceTypeManager,
    'discount': DiscountTypeManager
}


def type_manager_factory(option_or_type):
    """
    Returns a type manager based on the options type
    """

    return _type_manager_register[option_or_type.type if hasattr(option_or_type, 'type') else option_or_type]