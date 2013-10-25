
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.utils.translation import ugettext as _
from selvbetjening.businesslogic.events.decorators import suspend_automatic_attendee_price_updates

from selvbetjening.core.events.options.typemanager import type_manager_factory
from selvbetjening.core.events.models import Event, AttendState, OptionGroup, Attend, Selection

from selvbetjening.sadmin2.options.stypemanager import stype_manager_factory
from selvbetjening.sadmin2.forms import OptionGroupForm, SelectOptionType, SelectionTransferForm, SelectionTransferVerificationForm
from selvbetjening.sadmin2.decorators import sadmin_prerequisites
from selvbetjening.sadmin2 import menu

from generic import generic_create_view, apply_search_query


@sadmin_prerequisites
def event_selections(request, event_pk):

    event = get_object_or_404(Event, pk=event_pk)

    # TODO rewrite this to use annotations to reduce the number of db queries

    option_groups = []
    for option_group in event.optiongroups.prefetch_related('option_set'):
        options = []
        for option in option_group.option_set.all():
            count = option.selections.count()
            waiting = option.selections.filter(attendee__state=AttendState.waiting).count()
            accepted = option.selections.filter(attendee__state=AttendState.accepted).count()
            attended = option.selections.filter(attendee__state=AttendState.attended).count()

            suboptions = []
            for suboption in option.suboptions:
                scount = suboption.selections.count()
                swaiting = suboption.selections.filter(attendee__state=AttendState.waiting).count()
                saccepted = suboption.selections.filter(attendee__state=AttendState.accepted).count()
                sattended = suboption.selections.filter(attendee__state=AttendState.attended).count()
                suboptions.append((suboption, scount, swaiting, saccepted, sattended))

            options.append((option, suboptions, count, waiting, accepted, attended))

        option_groups.append((option_group, options))

    return render(request,
                  'sadmin2/event/selections.html',
                  {
                      'sadmin2_menu_main_active': 'events',
                      'sadmin2_breadcrumbs_active': 'event_selections',
                      'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
                      'sadmin2_menu_tab_active': 'selections',

                      'event': event,

                      'optiongroups': option_groups
                  })


@sadmin_prerequisites
def event_selections_manage(request, event_pk):

    FIELDS = (
        'in_scope_view_public',
        'in_scope_view_registration',
        'in_scope_view_manage',
        'in_scope_view_user_invoice',
        'in_scope_view_system_invoice',
        'in_scope_edit_registration',
        'in_scope_edit_manage_waiting',
        'in_scope_edit_manage_accepted',
        'in_scope_edit_manage_attended',
        'order'
    )

    GROUP_FIELDS = (
        'order',
    )

    event = get_object_or_404(Event, pk=event_pk)
    option_groups = event.optiongroups

    # Note, we could have used the standard django form framework for this, however it would be a mess
    # I only hope this is just a bit less messy :)

    if request.method == 'POST':

        # add anon option group

        if 'add-anon-group' in request.POST:

            if not event.has_special:

                OptionGroup.objects.create(
                    event=event,
                    is_special=True
                )

                messages.success(request, _('Special option group created'))
                return HttpResponseRedirect(reverse('sadmin2:event_selections_manage', kwargs={'event_pk': event.pk}))

        # split selections into options

        option_data = {}
        option_group_data = {}

        for key, value in request.POST.items():

            # all option data is formatted as field__pk and option_group data is formatted as field--pk
            if '__' in key:
                split = '__'
                data = option_data
            elif '--' in key:
                split = '--'
                data = option_group_data
            else:
                continue

            field, pk = key.split(split)
            pk = int(pk)

            data.setdefault(pk, {})
            data[pk][field] = value

        # update options

        def inject_data(object, fields, data):
            for field in fields:
                if field == 'order':
                    try:
                        setattr(object, field, int(data[object.pk][field]))
                    except KeyError:
                        pass  # race condition on new option?
                else:
                    setattr(object, field, object.pk in data and field in data[object.pk])

        for option_group in option_groups:

            inject_data(option_group, GROUP_FIELDS, option_group_data)
            option_group.save()

            for option in option_group.options:
                inject_data(option, FIELDS, option_data)
                option.save()

        messages.success(request, _('Selections saves'))
        return HttpResponseRedirect(reverse('sadmin2:event_selections_manage', kwargs={'event_pk': event.pk}))

    return render(request,
                  'sadmin2/event/selections_manage.html',
                  {
                      'sadmin2_menu_main_active': 'events',
                      'sadmin2_breadcrumbs_active': 'event_selections_manage',
                      'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
                      'sadmin2_menu_tab_active': 'selections',

                      'event': event,

                      'option_groups': option_groups
                  })


@sadmin_prerequisites
def event_selections_create_group(request, event_pk):

    event = get_object_or_404(Event, pk=event_pk)

    context = {
        'sadmin2_menu_main_active': 'events',
        'sadmin2_breadcrumbs_active': 'event_selections_create_group',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
        'sadmin2_menu_tab_active': 'selections',

        'event': event
    }

    def save_callback(instance):
        instance.event = event
        instance.save()

    return generic_create_view(request,
                               OptionGroupForm,
                               reverse('sadmin2:event_selections_manage', kwargs={'event_pk': event.pk}),
                               message_success=_('Option group created'),
                               context=context,
                               instance_save_callback=save_callback)


@sadmin_prerequisites
def event_selections_edit_group(request, event_pk, group_pk):

    event = get_object_or_404(Event, pk=event_pk)
    group = get_object_or_404(event.optiongroups, pk=group_pk)

    context = {
        'sadmin2_menu_main_active': 'events',
        'sadmin2_breadcrumbs_active': 'event_selections_edit_group',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
        'sadmin2_menu_tab_active': 'selections',

        'event': event,
        'option_group': group
    }

    return generic_create_view(request,
                               OptionGroupForm,
                               reverse('sadmin2:event_selections_manage', kwargs={'event_pk': event.pk}),
                               message_success=_('Option group saved'),
                               context=context,
                               instance=group)


@sadmin_prerequisites
def event_selections_create_option(request, event_pk, group_pk):

    event = get_object_or_404(Event, pk=event_pk)
    group = get_object_or_404(event.optiongroups, pk=group_pk)

    if request.method == 'POST':

        form = SelectOptionType(request.POST)

        if form.is_valid():
            return HttpResponseRedirect(reverse('sadmin2:event_selections_create_option_step2',
                                                kwargs={
                                                    'event_pk': event.pk,
                                                    'group_pk': group.pk,
                                                    'type_raw': form.cleaned_data['type']}))

    else:
        form = SelectOptionType()

    return render(
        request,
        'sadmin2/generic/form.html',
        {
            'sadmin2_menu_main_active': 'events',
            'sadmin2_breadcrumbs_active': 'event_selections_create_option',
            'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
            'sadmin2_menu_tab_active': 'selections',

            'event': event,
            'option_group': group,

            'form': form
        }
    )


@sadmin_prerequisites
def event_selections_create_option_step2(request, event_pk, group_pk, type_raw):

    event = get_object_or_404(Event, pk=event_pk)
    group = get_object_or_404(event.optiongroups, pk=group_pk)

    stype_manager = stype_manager_factory(type_raw)

    view = stype_manager.get_create_view()

    return view(request, event, group)


@sadmin_prerequisites
def event_selections_edit_option(request, event_pk, group_pk, option_pk):

    event = get_object_or_404(Event, pk=event_pk)
    group = get_object_or_404(event.optiongroups, pk=group_pk)
    _option = get_object_or_404(group.options, pk=option_pk)

    type_manager = type_manager_factory(_option)
    stype_manager = stype_manager_factory(_option)

    # fetch the correct "overloaded" option
    option = type_manager.get_model().objects.get(pk=_option.pk)

    view = stype_manager.get_update_view()

    return view(request, event, group, instance=option)


@sadmin_prerequisites
@suspend_automatic_attendee_price_updates
def event_selections_transfer(request, event_pk):

    event = get_object_or_404(Event, pk=event_pk)

    verification_mode = False
    selections = None

    if request.method == 'POST':
        form = SelectionTransferForm(request.POST, event=event)

        if form.is_valid():

            selections = Selection.objects.filter(option=form.cleaned_data['from_option'])

            if len(form.cleaned_data['status']) > 0:
                selections = selections.filter(attendee__state__in=form.cleaned_data['status'])

            if form.cleaned_data['from_suboption'] is not None:
                selections = selections.filter(suboption=form.cleaned_data['from_suboption'])

            if 'verify' in request.POST:

                attendees = []
                to_option = form.cleaned_data['to_option']
                to_suboption = form.cleaned_data['to_suboption']

                for selection in selections:
                    attendee = selection.attendee
                    attendees.append(attendee)

                    # delete old selection
                    selection.delete()

                    # select new selection
                    new_selection, created = Selection.objects.get_or_create(
                        attendee=attendee,
                        option=to_option,
                        suboption=to_suboption,
                        defaults={
                            'text': selection.text
                        }
                    )

                    # update price
                    attendee.price -= selection.price
                    if created:
                        attendee.price += new_selection.price
                    attendee.save()

                email = form.cleaned_data['email']

                if email is not None:
                    for attendee in attendees:
                        email.send_email_attendee(attendee, 'sadmin.selections.transfer')

                messages.success(request, _('Selections transferred'))
                return HttpResponseRedirect(reverse('sadmin2:event_selections', kwargs={'event_pk': event.pk}))

            else:
                # show verification form
                form = SelectionTransferVerificationForm(request.POST, event=event)
                verification_mode = True

    else:
        form = SelectionTransferForm(event=event)

    return render(
        request,
        'sadmin2/event/selections_transfer_step1.html',
        {
            'sadmin2_menu_main_active': 'events',
            'sadmin2_breadcrumbs_active': 'event_selections_transfer',
            'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
            'sadmin2_menu_tab_active': 'selections',

            'event': event,
            'selections': selections,
            'verification_mode': verification_mode,

            'form': form
        }
    )


