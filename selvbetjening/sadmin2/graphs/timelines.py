import datetime
import qsstats


def _is_empty(series):
    for s in series:
        for v in s['values']:
            if v['y'] > 0:
                return False

    return True


class SimpleGraph(object):
    datetime_xaxis = False

    def __init__(self, *args):
        self.series = [{
            'area': False,
            'label': '',
            'values': [
                {
                    'x': unit.label,
                    'y': unit.qs.count()
                } for unit in args
            ]
        }]

        self.empty = _is_empty(self.series)


class AbstractTimeGraph(object):

    class SCOPE:
        year = 'years'
        month = 'months'
        week = 'weeks'
        hour = 'hours'
        minute = 'minutes'

    def __init__(self, interval, *units, **kwargs):
        accumulative = kwargs.pop('accumulative', False)

        self.series = []

        for unit in units:

            start = unit.start_date
            end = unit.end_date

            qss = qsstats.QuerySetStats(unit.qs, unit.date_field)
            time_series = qss.time_series(start, end, interval=interval)

            if accumulative:
                time_series_acc = []

                for item in time_series:
                    try:
                        time_series_acc.append((item[0], item[1] + time_series_acc[-1][1]))
                    except IndexError:
                        # exception when time series is empty
                        assert len(time_series_acc) == 0
                        time_series_acc.append(item)

                self.series.append({
                    'area': False,
                    'label': '%s (acc.)' % unit.label,
                    'values': self.get_series_values(time_series_acc)
                })

            self.series.append({
                'area': True,
                'label': unit.label,
                'values': self.get_series_values(time_series)
            })

        self.empty = _is_empty(self.series)

    def get_series_values(self, time_series):
        raise NotImplementedError


class AbsoluteTimeGraph(AbstractTimeGraph):
    datetime_xaxis = True

    def get_series_values(self, time_series):
        return map(lambda x: {'x': x[0], 'y': x[1]}, time_series)


class RelativeTimeGraph(AbstractTimeGraph):
    datetime_xaxis = False

    def get_series_values(self, time_series):
        return map(lambda x, i: {'x': i, 'y': x[1]}, time_series, xrange(0, len(time_series)))


class AgeTimeGraph(AbstractTimeGraph):
    datetime_xaxis = False

    def __init__(self, *args, **kwargs):
        self.today = kwargs.pop('today', None)
        if self.today is None:
            self.today = datetime.datetime.now()

        super(AgeTimeGraph, self).__init__(*args, **kwargs)

    def get_series_values(self, time_series):
        time_series = list(reversed(time_series))  # We need to print values in the same order in which they are shown in the graph
        return map(lambda x, i: {'x': self.today.year - x[0].year, 'y': x[1]}, time_series, xrange(0, len(time_series)))
