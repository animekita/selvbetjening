import datetime

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from selvbetjening.data.accounting.models import Payment
from selvbetjening.data.events.models import Event

@login_required
def profile(request, template_name='members/profile.html'):
    attends = request.user.attend_set.all().order_by('-event__id')
    visited_keys = []
    for attend in attends:
        visited_keys.append(attend.event.id)

    return render_to_response(template_name,
                              {'membership_status' : Payment.objects.get_membership_state(request.user),
                               'membership_date' : Payment.objects.member_since(request.user),
                               'membership_to' : Payment.objects.member_to(request.user),
                               'membership_passive_to' : Payment.objects.passive_to(request.user),
                               'attends' : attends,
                               'events_new' : Event.objects.exclude(id__in=visited_keys).filter(enddate__gte=datetime.date.today()).filter(registration_open__exact=1) },
                              context_instance=RequestContext(request))

def profile_redirect(request):
    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect(reverse('members_login'))
    else:
        return HttpResponseRedirect(reverse('members_profile'))