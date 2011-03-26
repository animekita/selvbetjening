from datetime import date, timedelta

def diff_in_months(ref_date, date):
    return (date.year - ref_date.year) * 12 + (date.month - ref_date.month)

def diff_in_weeks(ref_date, date):
    first_week = int(ref_date.strftime('%W'))
    last_week = int(date.strftime('%W'))

    return (date.year - ref_date.year) * 52 + last_week - first_week

def accumulate(data):

    acc_sum = 0
    acc = []

    for value in data:
        acc_sum = acc_sum + value
        acc.append(acc_sum)

    return acc

def insert_prefix(data, axis=False):
    """
    Adds a prefix entry effectively forcing a initial zero state for the graphs.
    Should be applied to both axis and data.
    """

    data.insert(0, " " if axis else 0)
    return data

def generate_month_axis(start_date, end_date):
    labels = []

    months = diff_in_months(start_date, end_date)

    for x in range(0, months + 1):
        new_month = (start_date.month + x) % 12

        if new_month == 0:
            new_month = 1

        month = date(year=start_date.year + (start_date.month + x) / 12,
                     month=new_month,
                     day=1)

        labels.append(month.strftime("%B %Y"))

    return labels

def generate_week_axis(start_date, end_date):
    axis = []

    last_month = None

    for week in xrange(0, diff_in_weeks(start_date, end_date) + 1):
        current = start_date + timedelta(days=week*7)

        if last_month == current.month:
            axis.append('%s' % current.strftime('%W'))
        else:
            axis.append('%s - %s' % (current.strftime('%B'), current.strftime('%W')))
            last_month = current.month

    return axis