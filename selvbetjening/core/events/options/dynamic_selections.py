
from collections import OrderedDict

from django import forms
from django.db.models import Count, Q
import operator

from selvbetjening.core.events.options.scope import SCOPE
from selvbetjening.core.events.options.typemanager import type_manager_factory
from selvbetjening.core.events.models import Selection, Option, AttendState


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
        scope_filters = [Q(**{scope: True})]

        if scope == SCOPE.EDIT_MANAGE_WAITING or \
           scope == SCOPE.EDIT_MANAGE_ACCEPTED or \
           scope == SCOPE.EDIT_MANAGE_ATTENDED:

            scope_filters.append(Q(in_scope_view_manage=True))

        if scope == SCOPE.EDIT_REGISTRATION:
            scope_filters.append(Q(in_scope_view_registration=True))

        options = options.filter(reduce(operator.or_, scope_filters))  # Creates Q(..) | Q(..) | Q(..)

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


def _pack_id(namespace, id):
    return '%s_%s' % (namespace, id)


def _unpack_id(packed_id):
    return packed_id.split('_')


def dynamic_selections_formset_factory(scope, event, *args, **kwargs):

    # TODO view and edit scopes should be taken into account

    form_classes = []

    for option_group_pk, options in dynamic_options(scope, event, as_group_dict=True).items():
        form_classes.append(dynamic_selections_form_factory(scope, options[0][0].group, *args,
                                                            options=[option[0] for option in options],
                                                            **kwargs))

    def init(self, *args, **kwargs):
        if 'instance' in kwargs:
            kwargs['attendee'] = kwargs['instance']

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

    def len(self):
        return self.instances.__len__()

    def getitem(self, key):
        return self.instances[key]

    fields = {
        '__init__': init,
        'save': save,
        'is_valid': is_valid,
        '__iter__': iter,
        '__len__': len,
        '__getitem__': getitem
    }

    return type('OptionGroupSelectionsFormSet', (object,), fields)


def dynamic_selections_form_factory(scope, option_group_instance, helper_factory=None, options=None):

    if options is None:
        options = dynamic_options(scope, option_group_instance.event, option_group=option_group_instance)
        options = [option[0] for option in options]

    # TODO use selections from dynamic options

    def init(self, *args, **kwargs):
        self.attendee = kwargs.pop('attendee', None)
        self.attendee = kwargs.pop('instance', self.attendee)

        if self.attendee is not None:
            initial = {}

            selections = kwargs.pop('selections', None)

            if selections is None:
                selections = self.attendee.selection_set.all().select_related('option')

            for selection in selections:
                field_id = _pack_id('option', selection.option.pk)

                if field_id in self.type_widgets:
                    initial[field_id] = self.type_widgets[field_id].initial_value(selection)

            kwargs['initial'] = initial

        super(forms.Form, self).__init__(*args, **kwargs)

        if self.attendee is not None:
            for field_id, type_widget in self.type_widgets.items():

                if not self.type_widgets[field_id].is_editable(self.attendee):
                    self.fields[field_id].widget.attrs['disabled'] = "disabled"

    def save(self, *args, **kwargs):
        attendee = kwargs.pop('attendee', self.attendee)
        assert attendee is not None

        for key, save_callback in self.save_callbacks.items():
            save_callback(attendee, self.cleaned_data.get(key, None))

    def clean_callback(field_id, type_manager_callback):
        def inner(self):
            return type_manager_callback(self.cleaned_data.get(field_id, None))

        return inner

    fields = {
        'save_callbacks': {},
        '__init__': init,
        'save': save,
        'type_widgets': {},
        'readonly': {}
    }

    if helper_factory is not None:
        fields['helper'] = helper_factory(option_group_instance,
                                          [_pack_id('option', option.pk) for option in options])

    for option in options:
        widget = type_manager_factory(option).get_widget(scope, option)
        field_id = _pack_id('option', option.pk)

        fields[field_id] = widget.get_field()

        if scope == SCOPE.SADMIN or getattr(option, scope):  # The edit scope bit is set
            fields['clean_%s' % field_id] = clean_callback(field_id, widget.clean_callback)
            fields['save_callbacks'][field_id] = widget.save_callback
        else:  # The edit bit is not set, this is a view only option
            fields['clean_%s' % field_id] = lambda self: None
            fields['save_callbacks'][field_id] = lambda attendee, value: None
            fields[field_id].widget.attrs['disabled'] = 'disabled'

        fields['type_widgets'][field_id] = widget

    return type('OptionGroupSelectionsForm', (forms.Form,), fields)



