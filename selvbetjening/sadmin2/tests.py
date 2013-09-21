
from django.utils import unittest
from django.test import TestCase

from selvbetjening.core.events.models import Event

import filtering


class FilteringTestCase(TestCase):
    fixtures = ['sadmin2_test_fixtures.json']

    def test_parser_splitting(self):

        fragments = filtering.query_parser("alpha beta", [])
        assert len(fragments) == 2

        fragments = filtering.query_parser("alpha \"beta beta\"", [])
        assert len(fragments) == 2

        fragments = filtering.query_parser("alpha", [])
        assert len(fragments) == 1

        fragments = filtering.query_parser("", [])
        assert len(fragments) == 0

        fragments = filtering.query_parser(':description="Another event"', ['description'])
        assert len(fragments) == 1

        with self.assertRaises(ValueError):
            filtering.query_parser(':description="Another event"', [])

    def test_fragment_construction(self):

        fragments = filtering.query_parser("alpha", [])
        assert len(fragments) == 1
        assert not fragments[0].excludes
        assert fragments[0].fragment_type == filtering.TYPES.SEARCH_TERM

        fragments = filtering.query_parser("-alpha", [])
        assert len(fragments) == 1
        assert fragments[0].excludes
        assert fragments[0].fragment_type == filtering.TYPES.SEARCH_TERM

        fragments = filtering.query_parser(':description="Another event"', ['description'])
        assert len(fragments) == 1, fragments
        assert fragments[0].fragment_type == filtering.TYPES.CONDITION

    def test_fragment_filtering(self):

        events = Event.objects.all()
        assert events.count() == 2

        e = filtering.filter_queryset(events, '"Event 1"', search_fields=['title'])
        assert e.count() == 1

        e = filtering.filter_queryset(events, 'Event 1', search_fields=['title'])
        assert e.count() == 1

        e = filtering.filter_queryset(events, 'Event', search_fields=['title'])
        assert e.count() == 2

        e = filtering.filter_queryset(events, '"Event 1"', search_fields=['title', 'description'])
        assert e.count() == 1

        # one term matches event 1 and another matches event 2
        e = filtering.filter_queryset(events, '"Event 1" Another', search_fields=['title', 'description'])
        assert e.count() == 0

        e = filtering.filter_queryset(events, 'Event', search_fields=['title', 'description'])
        assert e.count() == 2

    def test_fragment_filtering_exclude_bit(self):

        events = Event.objects.all()
        assert events.count() == 2

        e = filtering.filter_queryset(events, '-Event', search_fields=['title', 'description'])
        assert e.count() == 0

        e = filtering.filter_queryset(events, '-"Event 1"', search_fields=['title', 'description'])
        assert e.count() == 1

        e = filtering.filter_queryset(events, '"Event 1" -"Event 1"', search_fields=['title', 'description'])
        assert e.count() == 0

    def test_fragment_filtering_condition(self):

        events = Event.objects.all()
        assert events.count() == 2

        e = filtering.filter_queryset(events, ':description="Another event"',
                                      search_fields=['title', 'description'],
                                      condition_fields=['description'])
        assert e.count() == 1

        with self.assertRaises(ValueError):
            filtering.filter_queryset(events, ':description="Another event"',
                                      search_fields=['title', 'description'])












