
from django.conf import settings

from django.shortcuts import render


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

