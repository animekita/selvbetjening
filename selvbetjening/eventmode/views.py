from datetime import datetime

from django import shortcuts
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.contrib.admin.views.main import ChangeList
from django.contrib.auth.models import User

from selvbetjening.accounting.forms import PaymentForm
from selvbetjening.accounting.models import MembershipState, Payment
from selvbetjening.core import logger
from selvbetjening.core.decorators import log_access
from selvbetjening.events.models import Event, Attend, Option

from decorators import eventmode_required
import checkin

def login(request, template_name='eventmode/login.html',
          success_page='eventmode_index'):

    message = None

    if request.method == 'POST':
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()

            # Get event and passphrase
            event = request.POST.get('event', None)
            passphrase = request.POST.get('passphrase', None)

            if event is not None and passphrase is not None:
                # Authenticate
                if request.eventmode.login(event, passphrase):
                    logger.info(request, 'client activated eventmode for event %s',
                                request.eventmode.model.event.id)

                    return HttpResponseRedirect(reverse(success_page))

                # If not authenticated, inform user
                else:
                    message = 'Det givne passphrase er ikke gyldigt for dette arrangement'

            # Missing credentials
            else:
                message = 'Angiv venligst arrangement og passphrase'

        # Cookies not supported, inform the user
        else:
            message = _("Looks like your browser isn't configured to accept cookies. Please enable cookies, reload this page, and try again.")

    request.session.set_test_cookie()
    return render_to_response(template_name,
                              {'events': Event.objects.all(),
                               'error_message' : message,},
                              context_instance=RequestContext(request))

def logout(request):
    request.eventmode.deactivate()

    return HttpResponseRedirect(reverse('home'))

@eventmode_required
def index(request, template='eventmode/index.html'):
    return render_to_response(template,
                              context_instance=RequestContext(request))

@eventmode_required
@log_access
def event_checkin(request, template_name='eventmode/checkin.html'):

    event = request.eventmode.model.event

    class DummyModelAdmin:
        ordering = None

        def queryset(self, request):
            return Attend.objects.filter(event=event)

    def checkin_link(attend):
        if not attend.has_attended:
            return '<a href="%s">checkin</a>' % reverse('eventmode_usercheckin',
                                                        kwargs={'user_id': attend.user.pk})
        else:
            return ''
    checkin_link.allow_tags = True
    checkin_link.short_description = _('Actions')

    cl = ChangeList(request, Attend,
                    ('user', 'user_first_name', 'user_last_name', 'has_attended', 'is_new', checkin_link),
                    ('username',),
                    ('has_attended',), (),
                    ('user__username', 'user__first_name', 'user__last_name'),
                    (), 50, DummyModelAdmin())

    return render_to_response(template_name,
                              {'attendees' : event.attendees,
                               'results' : event.attendees,
                               'event' : event,
                               'cl' : cl},
                              context_instance=RequestContext(request))

@eventmode_required
@log_access
def event_usercheckin(request, user_id,
                      template_name='eventmode/usercheckin.html'):

    event = request.eventmode.model.event
    attend = shortcuts.get_object_or_404(Attend, event=event, user=user_id)
    user = attend.user

    if attend.has_attended:
        return HttpResponseRedirect(reverse('eventmode_checkin'))

    # Run all checkin processors
    checkin_allowed_by_all = True
    render_functions = []
    for checkin_func in checkin.get_checkin_processors():
        checkin_allowed, render_func = checkin_func(request, user, event)

        if not checkin_allowed:
            checkin_allowed_by_all = False

        render_functions.append(render_func)

    # Check for checkin
    if request.method == 'POST' and request.POST.has_key('do_checkin'):
        if checkin_allowed_by_all:
            attend.has_attended = True
            attend.save()
            return HttpResponseRedirect(reverse('eventmode_checkin'))

    # Render the checkin parts
    checkin_parts = ''
    for render_func in render_functions:
        checkin_parts += render_func()

    return render_to_response(template_name,
                              {'user' : user,
                               'event' : event,
                               'attend' : attend,
                               'checkin_parts' : checkin_parts},
                              context_instance=RequestContext(request))

@eventmode_required
@log_access
def event_options(request, template_name='eventmode/options.html'):

    event = request.eventmode.model.event

    return render_to_response(template_name,
                              {'event' : event,
                               'optiongroups' : event.optiongroup_set.all()},
                              context_instance=RequestContext(request))

@eventmode_required
@log_access
def event_options_detail(request, option_id,
                             template_name='eventmode/options_detail.html'):

    option = get_object_or_404(Option, pk=option_id)

    return render_to_response(template_name,
                              {'event' : option.group.event, 'option' : option,
                               'users' : option.users.all()},
                              context_instance=RequestContext(request))

