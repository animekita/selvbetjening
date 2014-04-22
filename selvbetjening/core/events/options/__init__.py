
def register_custom_type(type_id, display_name, typemanager):

    from selvbetjening.core.events.models.options import Option
    from selvbetjening.core.events.options.typemanager import _type_manager_register

    Option.TYPE_CHOICES.append((type_id, display_name))
    _type_manager_register[type_id] = typemanager