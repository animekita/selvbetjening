
from collections import OrderedDict

from django import forms
from django.db.models import Count

from models import Selection, Option, AttendState


class SCOPE:

    def __init__(self):
        raise Exception

    SADMIN = None

    VIEW_REGISTRATION = 'in_scope_view_registration'
    VIEW_MANAGE = 'in_scope_view_manage'
    VIEW_USER_INVOICE = 'in_scope_view_user_invoice'
    VIEW_SYSTEM_INVOICE = 'in_scope_view_system_invoice'

    EDIT_REGISTRATION = 'in_scope_edit_registration'
    EDIT_MANAGE_WAITING = 'in_scope_edit_manage_waiting'
    EDIT_MANAGE_ACCEPTED = 'in_scope_edit_manage_accepted'
    EDIT_MANAGE_ATTENDED = 'in_scope_edit_manage_attended'


def dynamic_statistics(event):
    """
    Returns public statistics for all options where in_scope_view_public == True
    """

    options = Option.objects.filter(group__event=event).filter(in_scope_view_public=True).\
        exclude(selection__attendee__state=AttendState.waiting).distinct().\
        annotate(confirmed_selections_count=Count('selection__pk')).\
        order_by('-group__is_special', 'group__order', 'order')

    return options


def dynamic_selections(scope, attendee, option_group=None, as_dict=False, as_group_dict=False):
    return _dynamic_selections(scope, attendee.event, attendee=attendee, option_group=option_group, as_dict=as_dict, as_group_dict=as_group_dict)


def dynamic_options(scope, event, option_group=None, as_dict=False, as_group_dict=False):
    return _dynamic_selections(scope, event, option_group=option_group, as_dict=as_dict, as_group_dict=as_group_dict)


def _dynamic_selections(scope, event, attendee=None, option_group=None, as_dict=False, as_group_dict=False):
    """
    Generates a list of options and selections for an event.

    This function respects scoping.

    Returns a list of (option, selection) tuples clustered in option groups and
    ordered according to option group and option ordering.

    If attendee is None then selection is always None

    If as_dict is True then it is returned as an ordered dictionary with option.pk as key.
    If as_group_dict is True then it is returned as an ordered dictionary with option_group.pk as key.
    """

    assert not (as_dict and as_group_dict)

    # get options

    options = Option.objects.filter(group__event=event).select_related('group')

    if not scope == SCOPE.SADMIN:
        options = options.filter(**{scope: True})

    if option_group is not None:
        options = options.filter(group=option_group)

    options = options.order_by('-group__is_special', 'group__order', 'order')

    # append selections

    if attendee is not None:
        selections = Selection.objects.filter(attendee=attendee)\
            .filter(option__in=options)\
            .select_related('option', 'option__group')
    else:
        selections = []

    # format result

    result = OrderedDict()

    for option in options:
        result[option.pk] = [option, None]

    for selection in selections:
        result[selection.option.pk][1] = selection

    if as_dict:
        return result

    elif as_group_dict:

        group_result = OrderedDict()

        for item in result.values():
            group_result.setdefault(item[0].group.pk, [])
            group_result[item[0].group.pk].append(item)

        return group_result

    else:
        return result.values()


def dynamic_selections_formset_factory(scope, event, *args, **kwargs):

    # TODO view and edit scopes should be taken into account

    form_classes = []

    for option_group_pk, options in dynamic_options(scope, event, as_group_dict=True).items():
        form_classes.append(dynamic_selections_form_factory(scope, options[0][0].group, *args,
                                                            options=[option[0] for option in options],
                                                            **kwargs))

    def init(self, *args, **kwargs):
        if 'attendee' in kwargs:
            # prefetch
            kwargs['selections'] = kwargs['attendee'].selection_set.all().select_related('option')

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


def dynamic_selections_form_factory(scope, option_group_instance, helper_factory=None, options=None):

    if options is None:
        options = dynamic_options(scope, option_group_instance.event, option_group=option_group_instance)
        options = [option[0] for option in options]

    # TODO use selections from dynamic options

    def init(self, *args, **kwargs):
        self.attendee = kwargs.pop('attendee', None)

        if self.attendee is not None:
            initial = {}

            selections = kwargs.pop('selections', None)

            if selections is None:
                selections = self.attendee.selection_set.all().select_related('option')

            for selection in selections:
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
                                          [_pack_id('option', option.pk) for option in options])

    for option in options:
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