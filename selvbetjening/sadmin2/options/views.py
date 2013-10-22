import uuid
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.utils.translation import ugettext as _
from core.events.models.options import DiscountCode

from selvbetjening.core.events.models import Option

from selvbetjening.sadmin2.decorators import sadmin_prerequisites
from selvbetjening.sadmin2 import menu

from selvbetjening.sadmin2.options.forms import SubOptionFormset, GenerateDiscountCodes, OptionForm, DiscountOptionForm


def base_option_update_view(type, form_class, show_suboptions=False):

    @sadmin_prerequisites
    def inner(request, event, group, instance):

        if show_suboptions:
            formset_class = SubOptionFormset
        else:
            formset_class = None

        if request.method == 'POST':

            form = form_class(request.POST, type=type, instance=instance)
            formset = formset_class(request.POST, instance=instance) if formset_class is not None else None

            if form.is_valid() and (formset is None or formset.is_valid()):

                option = form.save(commit=False)
                option.type = type
                option.group = group
                option.save()

                if formset is not None:
                    formset.save()
                messages.success(request, _('Option saved'))

                return HttpResponseRedirect(
                    reverse('sadmin2:event_selections_edit_option',
                            kwargs={'event_pk': event.pk,
                                    'group_pk': group.pk,
                                    'option_pk': option.pk})
                )
        else:
            form = form_class(type=type, instance=instance)
            formset = SubOptionFormset(instance=instance) if formset_class is not None else None

        return render(
            request,
            'sadmin2/event/selection_option_update.html',
            {
                'sadmin2_menu_main_active': 'events',
                'sadmin2_breadcrumbs_active': 'event_selections_edit_option',
                'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
                'sadmin2_menu_tab_active': 'selections',

                'form': form,
                'formset': formset,

                'event': event,
                'option_group': group,
                'option': instance
            })

    return inner


def base_option_create_view(type, form_class):

    @sadmin_prerequisites
    def inner(request, event, group):

        if request.method == 'POST':

            form = form_class(request.POST, type=type)

            if form.is_valid():

                option = form.save(commit=False)
                option.type = type
                option.group = group
                option.save()

                messages.success(request, _('Option created'))

                return HttpResponseRedirect(
                    reverse('sadmin2:event_selections_edit_option',
                            kwargs={'event_pk': event.pk,
                                    'group_pk': group.pk,
                                    'option_pk': option.pk})
                )

        else:
            form = form_class(type=type)

        return render(
            request,
            'sadmin2/event/selection_option_update.html',
            {
                'sadmin2_menu_main_active': 'events',
                'sadmin2_breadcrumbs_active': 'event_selections_create_option',
                'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
                'sadmin2_menu_tab_active': 'selections',

                'form': form,

                'event': event,
                'option_group': group
            })

    return inner


@sadmin_prerequisites
def discount_option_update_view(request, event, group, instance):

    if request.method == 'POST' and 'save' in request.POST:

        form = DiscountOptionForm(request.POST, instance=instance)
        formset = SubOptionFormset(request.POST, instance=instance)

        if form.is_valid() and formset.is_valid():

            form.save()
            formset.save()
            messages.success(request, _('Option saved'))

    else:
        form = DiscountOptionForm(instance=instance)
        formset = SubOptionFormset(instance=instance)

    if request.method == 'POST' and 'gen' in request.POST:

        gen_form = GenerateDiscountCodes(request.POST)

        if gen_form.is_valid():

            for i in xrange(0, gen_form.cleaned_data['amount']):

                prefix = gen_form.cleaned_data['prefix'].upper()
                code = '%s.%s' % (prefix, uuid.uuid4().hex[:14])

                DiscountCode.objects.create(
                    discount_option=instance,
                    code=code
                )

    else:
        gen_form = GenerateDiscountCodes()

    discount_codes = DiscountCode.objects.filter(discount_option=instance).select_related()

    return render(
        request,
        'sadmin2/event/selection_discount_option_update.html',
        {
            'sadmin2_menu_main_active': 'events',
            'sadmin2_breadcrumbs_active': 'event_selections_edit_option',
            'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
            'sadmin2_menu_tab_active': 'selections',

            'form': form,
            'formset': formset,
            'gen_form': gen_form,

            'discount_codes': discount_codes,

            'event': event,
            'option_group': group,
            'option': instance
        })


@sadmin_prerequisites
def discount_option_create_view(request, event, group):

    if request.method == 'POST':

        form = DiscountOptionForm(request.POST)

        if form.is_valid():

            option = form.save(commit=False)
            option.type = 'discount'
            option.group = group
            option.save()

            messages.success(request, _('Option created'))

            return HttpResponseRedirect(
                reverse('sadmin2:event_selections_edit_option',
                        kwargs={'event_pk': event.pk,
                                'group_pk': group.pk,
                                'option_pk': option.pk}))

    else:
        form = DiscountOptionForm()

    return render(
        request,
        'sadmin2/generic/form.html',
        {
            'sadmin2_menu_main_active': 'events',
            'sadmin2_breadcrumbs_active': 'event_selections_create_option',
            'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
            'sadmin2_menu_tab_active': 'selections',

            'form': form,

            'event': event,
            'option_group': group
        })
