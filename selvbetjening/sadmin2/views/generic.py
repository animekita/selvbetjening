from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from sadmin2.decorators import sadmin_prerequisites
from selvbetjening.sadmin2 import filtering


def apply_search_query(qs, query, search_fields, condition_fields=None):

    if condition_fields is None:
        condition_fields = []

    invalid_fragments = []
    return filtering.filter_queryset(qs, query, search_fields, condition_fields, invalid_fragments=invalid_fragments), invalid_fragments


@sadmin_prerequisites
def generic_create_view(request,
                        form_class,
                        redirect_success_url,
                        message_success=None,
                        context=None,
                        instance=None,
                        instance_save_callback=None,
                        template=None):

    instance_kwarg = {} if instance is None else {'instance': instance}

    if request.method == 'POST':

        form = form_class(request.POST, **instance_kwarg)

        if form.is_valid():

            if instance_save_callback is None:
                form.save()

            else:
                instance = form.save(commit=False)
                instance_save_callback(instance)

            if message_success is not None:
                messages.success(request, message_success)

            return HttpResponseRedirect(redirect_success_url)

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
                context=None):

    if search_columns is None:
        search_columns = []

    if search_conditions is None:
        search_conditions = []

    if context is None:
        context = {}

    query = request.GET.get('q', '')

    queryset, invalid_fragments = apply_search_query(queryset, query, search_columns, condition_fields=search_conditions)

    paginator = Paginator(queryset, 30)
    page = request.GET.get('page')

    try:
        instances = paginator.page(page)
    except PageNotAnInteger:
        instances = paginator.page(1)
    except EmptyPage:
        instances = paginator.page(paginator.num_pages)

    context.update({
        'instances': instances,
        'invalid_fragments': invalid_fragments,

        'query': query,
        'search_url': request.path_info + '?q='
    })

    return render(request,
                  template_page if not request.is_ajax() else template_fragment,
                  context)
