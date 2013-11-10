
from selvbetjening.core.events.models import Option

from selvbetjening.sadmin2.options.forms import option_form_factory, UpdateAutoSelectChoiceOptionForm, \
    CreateAutoSelectChoiceOptionForm, CreateDiscountOptionForm
from selvbetjening.sadmin2.options.views import base_option_update_view, discount_option_update_view, \
    base_option_create_view


class SBaseTypeManager(object):

    def __init__(self, type_raw,
                 update_show_suboptions=False,
                 update_form=None,
                 create_form=None):

        self.update_show_suboptions = update_show_suboptions

        self.create_form = option_form_factory(
            Option,
            ('name', 'description', 'required', 'depends_on', 'price'),
            ('name', 'type', 'description', 'required', 'depends_on', 'price'),
            type_raw
        ) if create_form is None else create_form

        self.update_form = option_form_factory(
            Option,
            ('name', 'description', 'required', 'depends_on'),
            ('name', 'type', 'description', 'required', 'depends_on', 'price'),
            type_raw
        ) if update_form is None else update_form

    def get_create_view(self):
        return base_option_create_view(
            self.create_form
        )

    def get_update_view(self):
        return base_option_update_view(
            self.update_form,
            show_suboptions=self.update_show_suboptions
        )


class SDiscountTypeManager(SBaseTypeManager):

    def get_update_view(self):
        return discount_option_update_view


_type_manager_register = {
    'boolean': SBaseTypeManager('boolean'),
    'text': SBaseTypeManager('text'),
    'choices': SBaseTypeManager(
        'choices',
        update_show_suboptions=True
    ),
    'autoselect': SBaseTypeManager('autoselect'),
    'autoselectchoice': SBaseTypeManager(
        'autoselectchoice',
        update_show_suboptions=True,
        update_form=UpdateAutoSelectChoiceOptionForm,
        create_form=CreateAutoSelectChoiceOptionForm
    ),
    'discount': SDiscountTypeManager(
        'discount',
        update_show_suboptions=True,
        create_form=CreateDiscountOptionForm,
        update_form=option_form_factory(
            Option,
            ('name', 'description', 'depends_on'),
            ('name', 'type', 'description', 'price', 'depends_on'),
            'discount'
        )
    )
}


def stype_manager_factory(option_or_type):
    """
    Returns a type manager based on the options type
    """

    return _type_manager_register[option_or_type.type if hasattr(option_or_type, 'type') else option_or_type]