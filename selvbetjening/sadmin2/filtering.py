
import shlex
import operator

from django.db.models import Q, F


class FilterException(Exception):
    pass


class TYPES(object):

    SEARCH_TERM = 0
    CONDITION = 1


class SearchFragment(object):

    fragment_type = TYPES.SEARCH_TERM

    def __init__(self, term, negated=False):
        self.term = term
        self.negated = negated

    def filter_queryset(self, queryset, search_fields):

        fields_and_terms = [Q(**{'%s__icontains' % search_field: self.term}) for search_field in search_fields]
        or_terms = reduce(operator.or_, fields_and_terms)

        return queryset.filter(or_terms) if not self.negated else queryset.exclude(or_terms)


class ConditionFragment(object):

    EQUAL = 0
    NOT_EQUAL = 1
    LT = 2
    GT = 3

    fragment_type = TYPES.CONDITION

    def __init__(self, lhs, operator, rhs, negated=False):
        self.lhs = lhs
        self.operator = operator
        self.rhs = rhs
        self.negated = negated

        if self.operator == ConditionFragment.NOT_EQUAL:
            self.negated = not self.negated

    def filter_queryset(self, queryset, search_fields):

        if self.operator == ConditionFragment.EQUAL or self.operator == ConditionFragment.NOT_EQUAL:
            term = {self.lhs: self.rhs}
        elif self.operator == ConditionFragment.LT:
            lhs = self.lhs + '__lt'
            term = {lhs: self.rhs}
        elif self.operator == ConditionFragment.GT:
            lhs = self.lhs + '__gt'
            term = {lhs: self.rhs}
        else:
            raise FilterException

        return queryset.filter(**term) if not self.negated else queryset.exclude(**term)

OPERATORS = [
    (u'!=', ConditionFragment.NOT_EQUAL),
    (u'=', ConditionFragment.EQUAL),
    (u'<', ConditionFragment.LT),
    (u'>', ConditionFragment.GT)
]


def _is_field(raw_value):

    return len(raw_value) > 0 and raw_value[0] == ':'


def _is_related(raw_fragment):

    return len(raw_fragment) > 0 and raw_fragment[0:4] == 'has:'


def _parse_related(raw_fragment, negated, allowed_related):
    """
    Assumes that raw_fragment has been checked by is_related.
    """

    parts = raw_fragment.split(':')

    if len(parts) != 2:
        raise FilterException

    field = parts[1]

    if len(field) == 0 or field not in allowed_related:
        raise FilterException

    return ConditionFragment(field + '_set', ConditionFragment.NOT_EQUAL, None, negated=negated)


def _is_condition(raw_fragment):

    if len(raw_fragment) == 0:
        return False

    for operator_repr, _ in OPERATORS:
        if operator_repr in unicode(raw_fragment):
            return True

    return False


def _parse_condition(raw_fragment, negated, allowed_conditions):
    """
    Assumes that raw_fragment has been checked by is_condition.
    """

    operator_repr = None
    operator = None

    # Find the used operator

    for op in OPERATORS:
        operator_repr, operator = op
        if operator_repr in raw_fragment:
            break

    # Split it into a lhs and rhs

    parts = raw_fragment.split(operator_repr)

    if len(parts) != 2:
        raise FilterException

    lhs, rhs = parts

    if len(lhs) == 0 or len(rhs) == 0:
        raise FilterException

    # The lhs must be a field reference

    if not _is_field(lhs):
        raise FilterException

    # Ensure that field references are white listed

    if lhs[1:] not in allowed_conditions:
        raise FilterException

    if _is_field(rhs) and rhs[1:] not in allowed_conditions:
        raise FilterException

    # Convert field references

    lhs = lhs[1:]
    rhs = F(rhs[1:]) if _is_field(rhs) else rhs

    return ConditionFragment(lhs, operator, rhs, negated=negated)


def _parse_search_term(raw_fragment, negated):
    return SearchFragment(raw_fragment, negated=negated)


def _is_negated(raw_fragment):
    if len(raw_fragment) == 0:
        raise FilterException

    return raw_fragment[0] == '-'


def _parse_exclude(raw_fragment):
    """
    Assumes that raw_fragment has been checked by is_exclude..
    """

    return raw_fragment[1:]


def query_parser(query, allowed_conditions, allowed_related, invalid_fragments=None):
    """
    Parses a query string and returns a series of query fragments.

    A fragment represents a modification to a queryset and closely mimics what is allowed through the
    usual python API to querysets.

    This allows us to expose filtering capabilities directly to a user
    e.g. in the form of advanced search boxes or by links to subsets of data from other sadmin2 pages.

    Currently we support:

    SEARCH_TERM            := <alphanumeric>*
                            | " <alphanumeric-and-space>* "

    CONDITION              := FIELD =|!=|<|> FIELD|PRIMITIVE_VALUE

    FIELD                  := : DJANGO_FIELD

    NEGATION               := - SEARCH_TERM
                            | - CONDITION

    RELATED                := has RELATED_FIELD

    RELATED_FIELD          := : FIELD

    """

    raw_fragments = map(lambda s: s.decode('utf8'), shlex.split(query.encode('utf8')))

    fragments = []

    for raw_fragment in raw_fragments:

        try:
            negated = _is_negated(raw_fragment)

            if negated:
                raw_fragment = _parse_exclude(raw_fragment)

            if _is_condition(raw_fragment):
                fragments.append(_parse_condition(raw_fragment, negated, allowed_conditions))

            elif _is_related(raw_fragment):
                fragments.append(_parse_related(raw_fragment, negated, allowed_related))

            else:
                fragments.append(_parse_search_term(raw_fragment, negated))

        except FilterException as e:
            if invalid_fragments is None:
                raise e
            else:
                invalid_fragments.append(raw_fragment)

    return fragments


def filter_queryset(queryset,
                    query,
                    search_fields=None,
                    condition_fields=None,
                    related_sets=None,
                    invalid_fragments=None,
                    search_order=None):

    if search_fields is None and condition_fields is None:
        return queryset

    if search_fields is None:
        search_fields = []

    if condition_fields is None:
        condition_fields = []

    if related_sets is None:
        related_sets = []

    fragments = query_parser(query, condition_fields, related_sets, invalid_fragments=invalid_fragments)

    for fragment in fragments:
        queryset = fragment.filter_queryset(queryset, search_fields)

    if search_order is not None:
        queryset = queryset.order_by(search_order)

    return queryset.distinct()


