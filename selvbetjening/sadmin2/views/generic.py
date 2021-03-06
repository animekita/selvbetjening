from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.conf import settings

from selvbetjening.sadmin2.decorators import sadmin_prerequisites
from selvbetjening.sadmin2 import filtering


def apply_search_query(qs, query, search_fields, condition_fields=None, related_sets=None, search_order=None):

    if condition_fields is None:
        condition_fields = []

    invalid_fragments = []
    return filtering.filter_queryset(qs, query, search_fields, condition_fields, related_sets,
                                     invalid_fragments=invalid_fragments,
                                     search_order=search_order), invalid_fragments


@sadmin_prerequisites
def generic_create_view(request,
                        form_class,
                        redirect_success_url=None,
                        redirect_success_url_callback=None,
                        message_success=None,
                        context=None,
                        instance=None,
                        instance_save_callback=None,
                        template=None):

    instance_kwarg = {} if instance is None else {'instance': instance}

    if request.method == 'POST':

        form = form_class(request.POST, **instance_kwarg)

        if form.is_valid():

            commit = instance_save_callback is None
            instance = form.save(commit=commit)

            if not commit:
                instance_save_callback(instance)

            if message_success is not None:
                messages.success(request, message_success)

            if redirect_success_url is not None:
                return HttpResponseRedirect(redirect_success_url)

            if redirect_success_url_callback is not None:
                return HttpResponseRedirect(redirect_success_url_callback(instance))

    else:
        form = form_class(**instance_kwarg)

    if context is None:
        context = {}

    context['form'] = form

    return render(request,
                  'sadmin2/generic/form.html' if template is None else template,
                  context)


@sadmin_prerequisites
def search_view(request,
                queryset,
                template_page,
                template_fragment,
                search_columns=None,
                search_conditions=None,
                search_related=None,
                search_order=None,
                context=None):

    if search_columns is None:
        search_columns = []

    if search_conditions is None:
        search_conditions = []

    if search_related is None:
        search_related = []

    if context is None:
        context = {}

    query = request.GET.get('q', '')

    queryset, invalid_fragments = apply_search_query(queryset, query, search_columns,
                                                     condition_fields=search_conditions,
                                                     related_sets=search_related,
                                                     search_order=search_order)

    paginator = Paginator(queryset, 30)
    page = request.GET.get('page')

    try:
        instances = paginator.page(page)
    except PageNotAnInteger:
        instances = paginator.page(1)
    except EmptyPage:
        instances = paginator.page(paginator.num_pages)

    if getattr(settings, 'FORCE_SCRIPT_NAME', None) is None:
        prefix = ''
    else:
        prefix = settings.FORCE_SCRIPT_NAME

    context.update({
        'instances': instances,
        'invalid_fragments': invalid_fragments,

        'query': query,
        'search_url': '%s%s?q=' % (prefix, request.path_info)
    })

    return render(request,
                  template_page if not request.is_ajax() else template_fragment,
                  context)
