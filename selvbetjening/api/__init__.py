from django.contrib.admin.views.main import ChangeList
from django.core.paginator import Paginator

def api_search_filter(request, base_queryset, model, search_fields):
    class FakeModelAdmin(object):
        ordering = None

        def queryset(self, request):
            return base_queryset

        def get_paginator(self, request, queryset, per_page, orphans=0, allow_empty_first_page=True):
            return Paginator(queryset, per_page, orphans, allow_empty_first_page)

    changelist = ChangeList(request, model, [], [], None, None, search_fields, False, 100, False, FakeModelAdmin())

    return changelist.get_query_set()