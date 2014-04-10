import uuid
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.utils.translation import ugettext as _

from selvbetjening.core.events.models.options import DiscountCode
from selvbetjening.sadmin2.decorators import sadmin_prerequisites
from selvbetjening.sadmin2 import menu

from selvbetjening.sadmin2.options.forms import SubOptionFormset, GenerateDiscountCodes, UpdateDiscountOptionForm


def base_option_update_view(form_class, show_suboptions=False):

    @sadmin_prerequisites
    def inner(request, event, group, instance,
              template_name='sadmin2/event/selection_option_update.html',
              extra_context=None):

        if show_suboptions:
            formset_class = SubOptionFormset
        else:
            formset_class = None

        if request.method == 'POST':

            form = form_class(request.POST, instance=instance)
            formset = formset_class(request.POST, instance=instance) if formset_class is not None else None

            if form.is_valid() and (formset is None or formset.is_valid()):

                form.save()

                if formset is not None:
                    formset.save()
                messages.success(request, _('Option saved'))

                return HttpResponseRedirect(
                    reverse('sadmin2:event_selections_edit_option',
                            kwargs={'event_pk': event.pk,
                                    'group_pk': group.pk,
                                    'option_pk': instance.pk})
                )
        else:
            form = form_class(instance=instance)
            formset = SubOptionFormset(instance=instance) if formset_class is not None else None

        context = {
            'sadmin2_menu_main_active': 'events',
            'sadmin2_breadcrumbs_active': 'event_selections_edit_option',
            'sadmin2_menu_tab': menu.sadmin2_menu_tab_event,
            'sadmin2_menu_tab_active': 'settings',

            'form': form,
            'formset': formset,

            'event': event,
            'option_group': group,
            'option': instance
        }

        if extra_context is not None:
            context.update(extra_context)

        return render(request, template_name, context)

    return inner


def base_option_create_view(form_class):

    @sadmin_prerequisites
    def inner(request, event, group):

        if request.method == 'POST':

            form = form_class(request.POST)

            if form.is_valid():

                option = form.save(commit=False)
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
            form = form_class()

        return render(
            request,
            'sadmin2/event/selection_option_create.html',
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

    parent_view = base_option_update_view(UpdateDiscountOptionForm, show_suboptions=True)

    if request.method == 'POST' and 'gen' in request.POST:
        request.method = 'get'  # fake a get request for the parent view

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

    discount_codes = DiscountCode.objects.filter(discount_option=instance)\
        .select_related('selection', 'selection__attendee', 'selection__attendee__user')

    return parent_view(request, event, group, instance,
                       template_name='sadmin2/event/selection_discount_option_update.html',
                       extra_context={
                           'gen_form': gen_form,
                           'discount_codes': discount_codes
                       })

