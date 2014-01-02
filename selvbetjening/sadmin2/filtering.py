
import shlex
import operator

from django.db.models import Q


class FilterException(Exception):
    pass


class TYPES(object):

    SEARCH_TERM = 0
    CONDITION = 1


class SearchFragment(object):

    fragment_type = TYPES.SEARCH_TERM

    def __init__(self, term, excludes=False):
        self.term = term
        self.excludes = excludes

    def filter_queryset(self, queryset, search_fields):

        fields_and_terms = [Q(**{'%s__icontains' % search_field: self.term}) for search_field in search_fields]
        or_terms = reduce(operator.or_, fields_and_terms)

        return queryset.filter(or_terms) if not self.excludes else queryset.exclude(or_terms)


class ConditionFragment(object):

    fragment_type = TYPES.CONDITION

    def __init__(self, field, term, excludes=False):
        self.field = field
        self.term = term
        self.excludes = excludes

    def filter_queryset(self, queryset, search_fields):

        term = {self.field: self.term}
        return queryset.filter(**term) if not self.excludes else queryset.exclude(**term)


def _is_condition(raw_fragment):
    return len(raw_fragment) > 0 and raw_fragment[0] == ':'


def _parse_condition(raw_fragment, excludes, allowed_conditions):
    """
    Assumes that raw_fragment has been checked by is_condition.
    """

    raw_fragment = raw_fragment[1:]

    parts = raw_fragment.split('=')

    if len(parts) != 2:
        raise FilterException

    field, search_term = parts

    if len(field) == 0 or len(search_term) == 0:
        raise FilterException

    if field not in allowed_conditions:
        raise FilterException

    return ConditionFragment(field, search_term, excludes=excludes)


def _parse_search_term(raw_fragment, excludes):
    return SearchFragment(raw_fragment, excludes=excludes)


def _is_exclude(raw_fragment):
    if len(raw_fragment) == 0:
        raise FilterException

    return raw_fragment[0] == '-'


def _parse_exclude(raw_fragment):
    """
    Assumes that raw_fragment has been checked by is_exclude..
    """

    return raw_fragment[1:]


def query_parser(query, allowed_conditions, invalid_fragments=None):
    """
    Parses a query string and returns a series of query fragments.

    A fragment represents a modification to a queryset and closely mimics what is allowed through the
    usual python API to querysets.

    This allows us to expose filtering capabilities directly to a user
    e.g. in the form of advanced search boxes or by links to subsets of data from other sadmin2 pages.

    Currently we support:

    SEARCH_TERM            := <alphanumeric>*
                            | " <alphanumeric-and-space>* "

    CONDITION              := : FIELD = SEARCH_TERM

    FIELD                  := <alphanumeric-and-single-underscore>*
                            | <alphanumeric-and-single-underscore>* __ FIELD

    EXCLUDE                := - SEARCH_TERM
                            | - CONDITION

    """

    raw_fragments = map(lambda s: s.decode('utf8'), shlex.split(query.encode('utf8')))

    fragments = []

    for raw_fragment in raw_fragments:

        try:
            excludes = _is_exclude(raw_fragment)

            if excludes:
                raw_fragment = _parse_exclude(raw_fragment)

            if _is_condition(raw_fragment):
                fragments.append(_parse_condition(raw_fragment, excludes, allowed_conditions))

            else:
                fragments.append(_parse_search_term(raw_fragment, excludes))

        except FilterException:
            if invalid_fragments is None:
                raise FilterException
            else:
                invalid_fragments.append(raw_fragment)

    return fragments


def filter_queryset(queryset, query, search_fields=None, condition_fields=None, invalid_fragments=None):

    if search_fields is None and condition_fields is None:
        return queryset

    if search_fields is None:
        search_fields = []

    if condition_fields is None:
        condition_fields = []

    fragments = query_parser(query, condition_fields, invalid_fragments=invalid_fragments)

    for fragment in fragments:
        queryset = fragment.filter_queryset(queryset, search_fields)

    return queryset.distinct()


