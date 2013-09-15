
import operator

from django.db.models import Q


def apply_search_query(qs, query, columns):

    if query is None:
        return qs

    or_groups = []

    for term in [term.strip() for term in query.split()]:
        or_group = [Q(**{'%s__icontains' % column: term}) for column in columns]
        or_groups.append(reduce(operator.or_, or_group))

    if len(or_groups) > 0:
        return qs.filter(reduce(operator.and_, or_groups))

    return qs.distinct()


def get_search_url(request, base_url):
    # Dynamically construct a search url based on the current url
    # Ensure the query (q) is at the end of the url.
    # We do this to maintain any filters et. al. that we could have added to the current url.

    extra_params = request.GET.copy()
    extra_params.pop('q', None)

    search_url = base_url + '?' + extra_params.urlencode()

    if len(extra_params) > 0:
        search_url += '&q='
    else:
        search_url += 'q='

    return search_url