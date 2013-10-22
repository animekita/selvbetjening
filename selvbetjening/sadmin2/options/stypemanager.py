from sadmin2.options.forms import OptionForm, AutoSelectChoiceOptionForm
from selvbetjening.sadmin2.options.views import base_option_update_view, discount_option_update_view, \
    base_option_create_view, discount_option_create_view


class SBooleanTypeManager(object):

    @staticmethod
    def get_create_view():
        return base_option_create_view('boolean', OptionForm)

    @staticmethod
    def get_update_view():
        return base_option_update_view('boolean', OptionForm)


class STextTypeManager(object):

    @staticmethod
    def get_create_view():
        return base_option_create_view('text', OptionForm)

    @staticmethod
    def get_update_view():
        return base_option_update_view('text', OptionForm)


class SChoiceTypeManager(object):

    @staticmethod
    def get_create_view():
        return base_option_create_view('choices', OptionForm)

    @staticmethod
    def get_update_view():
        return base_option_update_view('choices', OptionForm, show_suboptions=True)


class SAutoSelectTypeManager(object):

    @staticmethod
    def get_create_view():
        return base_option_create_view('autoselect', OptionForm)

    @staticmethod
    def get_update_view():
        return base_option_update_view('autoselect', OptionForm)


class SAutoSelectChoiceTypeManager(object):

    @staticmethod
    def get_create_view():
        return base_option_create_view('autoselectchoice', AutoSelectChoiceOptionForm)

    @staticmethod
    def get_update_view():
        return base_option_update_view('autoselectchoice', AutoSelectChoiceOptionForm, show_suboptions=True)


class SDiscountTypeManager(object):

    @staticmethod
    def get_create_view():
        return discount_option_create_view

    @staticmethod
    def get_update_view():
        return discount_option_update_view

_type_manager_register = {
    'boolean': SBooleanTypeManager,
    'text': STextTypeManager,
    'choices': SChoiceTypeManager,
    'autoselect': SAutoSelectTypeManager,
    'autoselectchoice': SAutoSelectChoiceTypeManager,
    'discount': SDiscountTypeManager
}


def stype_manager_factory(option_or_type):
    """
    Returns a type manager based on the options type
    """

    return _type_manager_register[option_or_type.type if hasattr(option_or_type, 'type') else option_or_type]