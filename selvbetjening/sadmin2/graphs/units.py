import datetime
from django.core.exceptions import ObjectDoesNotExist

from selvbetjening.core.events.models import Attend, AttendState
from selvbetjening.core.user.models import SUser

"""
A unit must expose the following properties

    `label` A name identifying the source data.
    `qs` A queryset of the source data.
    `date_field` Name of the date field used for grouping a unit into a time series.
    `start_date` Start date of any time series.
    `end_date` End date of any time series.

"""


def _get_start_date(queryset, date_field):
    try:
        start_date = getattr(queryset.earliest(date_field), date_field)
        return start_date if start_date is not None else datetime.datetime.today()
    except ObjectDoesNotExist:
        return datetime.datetime.now()


def _get_end_date(queryset, date_field):
    try:
        end_date = getattr(queryset.latest(date_field), date_field)
        return end_date if end_date is not None else datetime.datetime.today()
    except ObjectDoesNotExist:
        return datetime.datetime.now()


class UserUnit(object):

    def __init__(self, label):
        self.label = label
        self.qs = SUser.objects.filter(date_joined__isnull=False)
        self.date_field = 'date_joined'
        self.start_date = _get_start_date(self.qs, self.date_field)
        self.end_date = _get_end_date(self.qs, self.date_field)


class UserAgeUnit(object):

    def __init__(self, label, today=None, max_age=80):

        if today is None:
            today = datetime.datetime.now()

        self.label = label
        self.qs = SUser.objects.filter(dateofbirth__isnull=False,
                                       dateofbirth__gt=today-datetime.timedelta(days=max_age*365.25))
        self.date_field = 'dateofbirth'
        self.start_date = _get_start_date(self.qs, self.date_field)
        self.end_date = _get_end_date(self.qs, self.date_field)
        self.today = today


class AttendeeRegisteredAgeUnit(object):

    def __init__(self, label, event, today, max_age=80):

        if today is None:
            today = datetime.datetime.today()

        self.label = label
        self.date_field = 'dateofbirth'
        self.qs = SUser.objects.filter(dateofbirth__isnull=False,
                                       dateofbirth__gt=today-datetime.timedelta(days=max_age*365.25),
                                       attend__event__pk=event.pk).distinct()
        self.start_date = _get_start_date(self.qs, self.date_field)
        self.end_date = _get_end_date(self.qs, self.date_field)


class AttendeeRegisteredUnit(object):

    def __init__(self, label, event):
        self.label = label
        self.date_field = 'registration_date'
        self.qs = Attend.objects.filter(event__pk=event.pk,
                                        registration_date__isnull=False)
        self.start_date = _get_start_date(self.qs, self.date_field)
        self.end_date = _get_end_date(self.qs, self.date_field)


class AttendeePaidUnit(object):

    def __init__(self, label, event):
        self.label = label
        self.date_field = 'change_timestamp'
        self.qs = Attend.objects.filter(event__pk=event.pk,
                                        change_timestamp__isnull=False,
                                        state__in=AttendState.accepted_states)
        self.start_date = _get_start_date(self.qs, self.date_field)
        self.end_date = _get_end_date(self.qs, self.date_field)


class AttendeeCheckedInUnit(object):

    def __init__(self, label, event):
        self.label = label
        self.date_field = 'changed'
        self.qs = Attend.objects.filter(event__pk=event.pk,
                                        changed__isnull=False,
                                        changed__gt=event.startdate if event.startdate is not None else datetime.datetime.now(),
                                        changed__lt=event.enddate if event.enddate is not None else datetime.datetime.now(),
                                        state=AttendState.attended)
        self.start_date = _get_start_date(self.qs, self.date_field)
        self.end_date = _get_end_date(self.qs, self.date_field)


class SelectionUnit(object):

    def __init__(self, label, option):
        self.label = label
        self.date_field = 'registration_date'
        self.qs = Attend.objects.filter(selection__option=option,
                                        registration_date__isnull=False)
        self.start_date = _get_start_date(self.qs, self.date_field)
        self.end_date = _get_end_date(self.qs, self.date_field)
