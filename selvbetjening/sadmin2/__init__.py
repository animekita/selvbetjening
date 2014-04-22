
def register_custom_stype(type_id, stypemanager):

    from selvbetjening.sadmin2.options.stypemanager import _stype_manager_register

    _stype_manager_register[type_id] = stypemanager