from selvbetjening.frontend.utilities.forms import S2Layout, S2Fieldset, S2FormHelper


def frontend_selection_helper_factory(option_group, visible_fields):

    description = option_group.description if option_group.description != '' else None

    layout = S2Layout(
        S2Fieldset(option_group.name, *visible_fields,
                   collapse=False,
                   show_help_text=True,
                   help_text=description)
    )

    helper = S2FormHelper(horizontal=True)
    helper.add_layout(layout)
    helper.form_tag = False

    return helper