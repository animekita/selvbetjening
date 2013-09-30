
from collections import OrderedDict

from django import forms

from models import Selection, Option


class SCOPE:
    def __init__(self):
        raise Exception

    VIEW_REGISTRATION = 'in_scope_view_registration'
    VIEW_MANAGE = 'in_scope_view_manage'
    VIEW_USER_INVOICE = 'in_scope_view_user_invoice'
    VIEW_SYSTEM_INVOICE = 'in_scope_view_system_invoice'

    EDIT_REGISTRATION = 'in_scope_edit_registration'
    EDIT_MANAGE_WAITING = 'in_scope_edit_manage_waiting'
    EDIT_MANAGE_ACCEPTED = 'in_scope_edit_manage_accepted'
    EDIT_MANAGE_ATTENDED = 'in_scope_edit_manage_attended'


def dynamic_selections(scope, event, attendee, option_group=None, as_dict=False):
    """
    Generates a list of options and attendee selections for an event.

    This function respects scoping.

    Returns tuples of (option, selection)
      where selection can be None

    The tuples are clustered according to their option groups, and respects ordering of
    option groups and options.

    If as_dict is True then it is returned as a dictionary with option.pk as key
    """

    selections = Selection.objects.filter(attendee=attendee, option__group__event=event)

    if option_group is not None:
        selections = selections.filter(option__group=option_group)

    options = Option.objects.filter(group__event=event).filter(**{scope: True})

    if option_group is not None:
        options = options.filter(group=option_group)

    options = options.order_by('-group__is_special', 'group__order', 'order')

    result = OrderedDict()

    for option in options:
        result[option.pk] = [option, None]

    for selection in selections:
        if selection.option.pk in result:
            result[selection.option.pk][1] = selection

    if as_dict:
        return result

    return result.values()


def dynamic_selections_formset_factory(event, *args, **kwargs):

    form_classes = []

    for option_group in event.optiongroups.all():
        form_classes.append(dynamic_selections_form_factory(option_group, *args, **kwargs))

    def init(self, *args, **kwargs):
        self.instances = [form_class(*args, **kwargs) for form_class in form_classes]

    def is_valid(self):
        return all([instance.is_valid() for instance in self.instances])

    def save(self, *args, **kwargs):
        for instance in self.instances:
            instance.save(*args, **kwargs)

    def iter(self):
        return self.instances.__iter__()

    fields = {
        '__init__': init,
        'save': save,
        'is_valid': is_valid,
        '__iter__': iter
    }

    return type('OptionGroupSelectionsFormSet', (object,), fields)


def dynamic_selections_form_factory(option_group_instance, helper_factory=None):

    def init(self, *args, **kwargs):
        self.attendee = kwargs.pop('attendee', None)

        if self.attendee is not None:
            initial = {}

            for selection in Selection.objects.filter(attendee=self.attendee).select_related('option'):
                if selection.option.type == 'boolean':
                    initial[_pack_id('option', selection.option.pk)] = True
                elif selection.option.type == 'text':
                    initial[_pack_id('option', selection.option.pk)] = selection.text
                elif selection.option.type == 'choices':
                    initial[_pack_id('option', selection.option.pk)] = _pack_id('suboption', selection.suboption.pk)
                else:
                    raise ValueError

            kwargs['initial'] = initial

        super(forms.Form, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        attendee = kwargs.pop('attendee', self.attendee)
        assert attendee is not None

        for key, save_callback in self.save_callbacks.items():
            save_callback(attendee, self.cleaned_data.get(key, None))

    fields = {
        'save_callbacks': {},
        '__init__': init,
        'save': save
    }

    if helper_factory is not None:
        fields['helper'] = helper_factory(option_group_instance,
                                          [_pack_id('option', option.pk) for option in option_group_instance.options])

    for option in option_group_instance.options:
        field_id, field, clean_callback, save_callback = _option_field_builder(option)

        fields[field_id] = field
        fields['clean_%s' % field_id] = clean_callback
        fields['save_callbacks'][field_id] = save_callback

    return type('OptionGroupSelectionsForm', (forms.Form,), fields)


def _pack_id(namespace, id):
    return '%s_%s' % (namespace, id)


def _unpack_id(packed_id):
    return packed_id.split('_')


def _option_field_builder(option):
    """
    Returns a forms.Field instance and a save callback

    (field_id, field, save_callback)
    """

    if option.type == 'boolean':
        return _option_field_builder_checkbox(option)
    elif option.type == 'text':
        return _option_field_builder_text(option)
    elif option.type == 'choices':
        return _option_field_builder_choices(option)
    else:
        raise ValueError


def _option_field_builder_checkbox(option):
    option_pk = option.pk

    field = forms.BooleanField(label=option.name,
                               required=False,
                               help_text=option.description,
                               widget=forms.CheckboxInput())

    def noop_save_callback(attendee, value):
        if value is not None and value:
            Selection.objects.get_or_create(
                option_id=option_pk,
                attendee=attendee
            )
        else:
            Selection.objects.filter(
                option_id=option_pk,
                attendee=attendee
            ).delete()

    def noop_clean_callback(self):
        return self.cleaned_data.get(_pack_id('option', option_pk), False)

    return (
        _pack_id('option', option.pk),
        field,
        noop_clean_callback,
        noop_save_callback
    )


def _option_field_builder_text(option):
    option_pk = option.pk

    field = forms.CharField(label=option.name,
                            required=False,
                            help_text=option.description,
                            widget=forms.TextInput())

    def noop_save_callback(attendee, value):
        if value is not None and len(value.strip()) > 0:
            selection, created = Selection.objects.get_or_create(
                option_id=option_pk,
                attendee=attendee
            )

            selection.text = value.strip()
            selection.save()
        else:
            Selection.objects.filter(
                option_id=option_pk,
                attendee=attendee
            ).delete()

    def noop_clean_callback(self):
        return self.cleaned_data.get(_pack_id('option', option_pk), False)

    return (
        _pack_id('option', option.pk),
        field,
        noop_clean_callback,
        noop_save_callback
    )


def _option_field_builder_choices(option):
    option_pk = option.pk

    choices = [('', '')] + [('suboption_%s' % suboption.pk, suboption.name)
                            for suboption in option.suboptions.all()]

    field = forms.ChoiceField(label=option.name,
                              required=False,
                              help_text=option.description,
                              widget=forms.Select(),
                              choices=choices)

    def noop_save_callback(attendee, value):
        if value is not None and len(value) > 0:
            selection, created = Selection.objects.get_or_create(
                option_id=option_pk,
                attendee=attendee
            )

            namespace, pk = _unpack_id(value)
            assert namespace == 'suboption'

            selection.suboption_id = pk
            selection.save()
        else:
            Selection.objects.filter(
                option_id=option_pk,
                attendee=attendee
            ).delete()

    def noop_clean_callback(self):
        return self.cleaned_data.get(_pack_id('option', option_pk), False)

    return (
        _pack_id('option', option.pk),
        field,
        noop_clean_callback,
        noop_save_callback
    )
