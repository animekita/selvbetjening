# coding=utf8

from django.utils import unittest
from django.test import TestCase

from selvbetjening.core.events.models import Event, Attend, AttendeeComment

from selvbetjening.sadmin2 import filtering


class FilteringTestCase(TestCase):
    fixtures = ['sadmin2_test_fixtures.json']

    def test_parser_splitting(self):

        fragments = filtering.query_parser("alpha beta", [], [])
        assert len(fragments) == 2

        fragments = filtering.query_parser("alpha \"beta beta\"", [], [])
        assert len(fragments) == 2

        fragments = filtering.query_parser("alpha", [], [])
        assert len(fragments) == 1

        fragments = filtering.query_parser("", [], [])
        assert len(fragments) == 0

        fragments = filtering.query_parser(':description="Another event"', ['description'], [])
        assert len(fragments) == 1

        with self.assertRaises(filtering.FilterException):
            filtering.query_parser(':description="Another event"', [], [])

    def test_fragment_construction(self):

        fragments = filtering.query_parser("alpha", [], [])
        assert len(fragments) == 1
        assert not fragments[0].negated
        assert fragments[0].fragment_type == filtering.TYPES.SEARCH_TERM

        fragments = filtering.query_parser("-alpha", [], [])
        assert len(fragments) == 1
        assert fragments[0].negated
        assert fragments[0].fragment_type == filtering.TYPES.SEARCH_TERM

        fragments = filtering.query_parser(':description="Another event"', ['description'], [])
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

        with self.assertRaises(filtering.FilterException):
            filtering.filter_queryset(events, ':description="Another event"',
                                      search_fields=['title', 'description'])

    def test_fragment_field_comparison(self):

        attendees = Attend.objects.all()
        assert attendees.count() == 1

        e = filtering.filter_queryset(attendees, ':price=:paid',
                                      search_fields=[],
                                      condition_fields=['price', 'paid'])
        assert e.count() == 0

        e = filtering.filter_queryset(attendees, '-:price=:paid',
                                      search_fields=[],
                                      condition_fields=['price', 'paid'])
        assert e.count() == 1

        e = filtering.filter_queryset(attendees, ':price!=:paid',
                                      search_fields=[],
                                      condition_fields=['price', 'paid'])
        assert e.count() == 1

        e = filtering.filter_queryset(attendees, ':price<:paid',
                                      search_fields=[],
                                      condition_fields=['price', 'paid'])
        assert e.count() == 0

        e = filtering.filter_queryset(attendees, ':price>:paid',
                                      search_fields=[],
                                      condition_fields=['price', 'paid'])
        assert e.count() == 1

    def test_fragment_lt_gt_comparison(self):

        attendees = Attend.objects.all()
        assert attendees.count() == 1

        e = filtering.filter_queryset(attendees, ':price<50',
                                      search_fields=[],
                                      condition_fields=['price', 'paid'])
        assert e.count() == 0

        e = filtering.filter_queryset(attendees, ':price>50',
                                      search_fields=[],
                                      condition_fields=['price', 'paid'])
        assert e.count() == 1

    def test_related(self):

        attendees = Attend.objects.all()
        assert attendees.count() == 1

        e = filtering.filter_queryset(attendees, 'has:comment',
                                      search_fields=[],
                                      related_sets=['comment'])
        assert e.count() == 0

        AttendeeComment.objects.create(
            attendee=attendees[0],
            author="author",
            comment="comment"
        )

        e = filtering.filter_queryset(attendees, 'has:comment',
                                      search_fields=[],
                                      related_sets=['comment'])
        assert e.count() == 1

    def test_non_ascii(self):

        events = Event.objects.all()
        assert events.count() == 2

        filtering.filter_queryset(events, u'ø :description=ø',
                                  search_fields=['title', 'description'],
                                  condition_fields=['description'])
