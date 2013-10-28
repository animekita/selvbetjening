from datetime import date
from django.conf import settings

from django.db.models import Max, Min
from django.shortcuts import render

from selvbetjening.core.members.models import UserLocation
from selvbetjening.core.user.models import to_age, SUser
from selvbetjening.sadmin2 import graph, menu
from selvbetjening.sadmin2.decorators import sadmin_prerequisites


def user_age_chart(users, min_age=5, max_age=80):

    cur_year = date.today().year

    # The graph looks stupid if we allow ages 0 and 100 et al.
    # Enforce sane limitations, lets say min 5 and max 80 years of age

    users = users.select_related()\
        .filter(dateofbirth__lt=date(cur_year-min_age, 1, 1))\
        .filter(dateofbirth__gt=date(cur_year-max_age, 1, 1))

    if users.count() == 0:
        return None

    age_stats = users.aggregate(min=Max('dateofbirth'),
                                max=Min('dateofbirth'))

    age_stats['max'], age_stats['min'] = (to_age(age_stats['max']),
                                          to_age(age_stats['min']))

    age_span = [0] * (age_stats['max'] - age_stats['min'] + 1)

    sum = count = 0
    for user in users:
        age = user.get_age()

        age_span[age - age_stats['min']] += 1
        sum += age
        count += 1

    return {
        'age_labels': range(age_stats['min'], age_stats['max'] + 1),
        'age_data': age_span,
        'min': age_stats['min'],
        'max': age_stats['max'],
        'avg': float(sum)/float(count),
        'max_limit': max_age,
        'min_limit': min_age
    }


def user_join_chart(users):

    if users.count() == 0:
        return None

    join_stats = users.aggregate(max=Max('date_joined'),
                                 min=Min('date_joined'))

    max_in_months = graph.diff_in_months(join_stats['min'], join_stats['max'])

    join_span = [0] * (max_in_months + 1)

    for user in users:
        join_month = graph.diff_in_months(join_stats['min'], user.date_joined)

        join_span[join_month] += 1

    join_span_acc = []
    acc = 0
    for item in join_span:
        acc += item
        join_span_acc.append(acc)

    labels = graph.generate_month_axis(join_stats['min'], join_stats['max'])

    return {'join_labels': labels,
            'join_data1': join_span,
            'join_data2': join_span_acc}


def insecure_reports_age(request,
                         users,
                         extra_context=None):

    join_data = user_join_chart(users)
    age_data = user_age_chart(users)

    if join_data is None:
        join_data = {}

    if age_data is None:
        age_data = {}

    context = {}
    context.update(age_data)
    context.update(join_data)

    if extra_context is not None:
        context.update(extra_context)

    return render(request,
                  'sadmin2/reports/age.html',
                  context)


def insecure_reports_address(request, userlocations, extra_context=None):

    locations = userlocations.exclude(lat=None, lng=None).exclude(expired=True).select_related()
    expired = userlocations.filter(expired=True).count()
    invalid = userlocations.filter(expired=False).count() - locations.count()

    map_key = getattr(settings, 'MAP_KEY', None)

    context = {
        'locations': locations,
        'expired': expired,
        'invalid': invalid,
        'map_key': map_key
    }

    if extra_context is not None:
        context.update(extra_context)

    return render(request,
                  'sadmin2/reports/address.html',
                  context)

