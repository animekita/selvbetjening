
from collections import OrderedDict

from django import forms
from django.db.models import Count, Q
import operator
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

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
    return _dynamic_selections(scope,
                               attendee.event,
                               attendee=attendee,
                               option_group=option_group,
                               as_dict=as_dict,
                               as_group_dict=as_group_dict)


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
            .select_related('option', 'option__group', 'suboption')
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

    @staticmethod
    def is_empty():
        return all([form_class.is_empty() for form_class in form_classes])

    fields = {
        '__init__': init,
        'save': save,
        'is_valid': is_valid,
        '__iter__': iter,
        '__len__': len,
        '__getitem__': getitem,
        'is_empty': is_empty
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
        self.user = kwargs.pop('user')

        if self.attendee is not None:
            self.user = self.attendee.user  # force the usage of attendee.user

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

        for field_id, type_widget in self.type_widgets.items():

            if hasattr(type_widget, 'update_choices'):
                type_widget.update_choices(self.user, self.attendee)
                self.fields[field_id].choices = type_widget.choices

            if self.attendee is not None and not type_widget.is_editable(self.attendee):
                self.fields[field_id].widget.attrs['disabled'] = "disabled"

    def save(self, *args, **kwargs):
        attendee = kwargs.pop('attendee', self.attendee)
        assert attendee is not None

        for key, save_callback in self.save_callbacks.items():
            save_callback(attendee, self.cleaned_data.get(key, None))

    def clean_callback(field_id, related_field, type_manager_clean_callback):
        def inner(self):

            # If we have a related field, then erase the value if the related field is not selected.
            if related_field is not None:

                # Related field is readonly and is not set "initially"
                if related_field in self.readonly and not self.initial.get(related_field, False):
                    return None

                if related_field not in self.readonly and not self.cleaned_data.get(related_field, False):
                    return None

            return type_manager_clean_callback(self.cleaned_data.get(field_id, None))

        return inner

    @staticmethod
    def is_empty():
        return len(options) == 0

    def clean(self):
        cleaned_data = super(forms.Form, self).clean()

        if scope == SCOPE.SADMIN:
            # Do not enforce max/min for admin
            return cleaned_data

        if option_group_instance.minimum_selected <= 0 and option_group_instance.maximum_selected <= 0:
            return cleaned_data

        selected = 0

        for option in options:
            field_id = _pack_id('option', option.pk)

            if getattr(option, scope):
                # field is editable
                value = cleaned_data.get(field_id, None)
            else:
                value = self.initial[field_id]

            selected += 1 if self._selected_callbacks[field_id](value) else 0

        if option_group_instance.minimum_selected > 0 and selected < option_group_instance.minimum_selected:
            raise forms.ValidationError(ungettext_lazy('You must select at least %d option.',
                                                       'You must select at least %d options.',
                                                       option_group_instance.minimum_selected) % option_group_instance.minimum_selected)

        if 0 < option_group_instance.maximum_selected < selected:
            raise forms.ValidationError(ungettext_lazy('You must select at most %d option.',
                                                       'You must select at most %d options.',
                                                       option_group_instance.maximum_selected) % option_group_instance.maximum_selected)

        return cleaned_data

    fields = {
        '__init__': init,
        'save': save,
        'is_empty': is_empty,
        'clean': clean,
        'save_callbacks': {},
        '_selected_callbacks': {},
        'type_widgets': {},
        'readonly': []
    }

    for option in options:
        widget = type_manager_factory(option).get_widget(scope, option)
        field_id = _pack_id('option', option.pk)

        related_field = None
        attrs = None

        if option.depends_on is not None:
            related_field = _pack_id('option', option.depends_on.pk)
            attrs = {'data-depends-on': related_field}

        fields[field_id] = widget.get_field(attrs=attrs)
        fields['_selected_callbacks'][field_id] = widget.selected_callback

        if scope == SCOPE.SADMIN or getattr(option, scope):  # The edit scope bit is set
            fields['clean_%s' % field_id] = clean_callback(field_id, related_field, widget.clean_callback)
            fields['save_callbacks'][field_id] = widget.save_callback
        else:  # The edit bit is not set, this is a view only option
            fields['clean_%s' % field_id] = lambda self: None
            fields['save_callbacks'][field_id] = lambda attendee, value: None

            if not hasattr(fields[field_id].widget, 'CANT_DISABLE'):
                fields[field_id].widget.attrs['disabled'] = 'disabled'
                fields[field_id].required = False  # If we don't do this Django will err because of missing POST data
                fields['readonly'].append(field_id)

        fields['type_widgets'][field_id] = widget

    if helper_factory is not None:
        fields['helper'] = helper_factory(option_group_instance,
                                          [_pack_id('option', option.pk) for option in options])

    return type('OptionGroupSelectionsForm', (forms.Form,), fields)



