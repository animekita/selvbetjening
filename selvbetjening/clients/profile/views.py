import datetime

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from selvbetjening.data.events.models import Event

from processor_handlers import viewprofile as viewprofile_handler

@login_required
def profile(request, template_name='profile/profile.html'):
    attends = request.user.attend_set.all().order_by('-event__id')
    visited_keys = []

    for attend in attends:
        visited_keys.append(attend.event.id)

    submit_allowed, render_functions, save_functions = \
                  viewprofile_handler.run_processors(request.user)

    add_to_profile = ''
    for render_function in render_functions:
        add_to_profile += render_function()

    return render_to_response(template_name,
                              {'attends' : attends,
                               'events_new' : Event.objects.exclude(id__in=visited_keys).filter(enddate__gte=datetime.date.today()).filter(registration_open__exact=1),
                               'add_to_profile' : add_to_profile,},
                              context_instance=RequestContext(request))

def profile_redirect(request):
    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect(reverse('members_login'))
    else:
        return HttpResponseRedirect(reverse('members_profile'))