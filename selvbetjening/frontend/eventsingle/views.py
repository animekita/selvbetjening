# encoding: utf-8

"""
    EventSingle implements a 5 step event registration workflow.

    Step 0: Login or (minimal) user account registration
    Step 1: Update user account information (new and existing users)
    Step 2: Event registration (select options)
    Step 3: Event payment
    Step 4: Event status page

"""

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

from selvbetjening.core.user.models import SUser
from selvbetjening.frontend.eventportal.views import event_register

from selvbetjening.core.events.models import Attend, AttendState

from selvbetjening.businesslogic.members.forms import MinimalUserRegistrationForm, ProfileEditForm
from selvbetjening.businesslogic.events.decorators import event_registration_open_required, \
    get_event_from_id, suspend_automatic_attendee_price_updates

from selvbetjening.frontend.auth.forms import AuthenticationForm
from selvbetjening.frontend.eventportal import views as eventportal_views


def _get_step(request, event_pk):
    # step 0 - user not logged in
    if not request.user.is_authenticated():
        return 0

    # step 1 or 2 - user not attending event
    try:
        attendee = Attend.objects.get(user=request.user, event__pk=event_pk)
    except Attend.DoesNotExist:

        # step 1 - verify user data
        if not request.session.get('user-data-verified', False):
            return 1

        return 2

    # step 3 - user not accepted
    if attendee.state == AttendState.waiting:
        return 3

    # step 4
    return 4


def step_controller(request, event_pk):

    step = _get_step(request, event_pk)

    if step == 0:
        return step0(request, event_pk)

    if step == 1:
        return step1(request, event_pk)

    elif step == 2:
        return step2(request, event_pk)

    elif step == 3:
        return step3(request, event_pk)

    return step4(request, event_pk)


@get_event_from_id
@event_registration_open_required
@suspend_automatic_attendee_price_updates
def step0(request, event):
    """
    Combined account creation and account login
    """

    handle_login = False
    handle_registration = False

    if request.method == 'POST':
        if 'submit_login' in request.POST:
            handle_login = True
        else:
            handle_registration = True

    if handle_registration:
        registration_form = MinimalUserRegistrationForm(request.POST)

        if registration_form.is_valid():
            user = registration_form.save()

            user_obj = authenticate(username=user.username,
                                    password=registration_form.cleaned_data['password'])
            login(request, user_obj)

            return HttpResponseRedirect(reverse('eventsingle_steps', kwargs={'event_pk': event.pk}))
    else:
        registration_form = MinimalUserRegistrationForm()

    if handle_login:
        login_form = AuthenticationForm(data=request.POST)

        if login_form.is_valid():

            login(request, login_form.get_user())
            return HttpResponseRedirect(reverse('eventsingle_steps', kwargs={'event_pk': event.pk}))

    else:
        login_form = AuthenticationForm()

    return render(request, 'eventsingle/step0.html',
                  {
                      'event': event,

                      'authentication_form': login_form,
                      'registration_form': registration_form,

                      'handle_authentication': handle_login,
                      'handle_registration': handle_registration,

                      'step': 0
                  })

@get_event_from_id
@event_registration_open_required
@suspend_automatic_attendee_price_updates
@login_required
def step1(request,
          event,
          form_class=ProfileEditForm):

    user = request.user

    if request.method == 'POST':
        form = form_class(request.POST, instance=user)

        if form.is_valid():
            form.save()

            request.session['user-data-verified'] = True
            return HttpResponseRedirect(reverse('eventsingle_steps', kwargs={'event_pk': event.pk}))

    else:
        form = form_class(instance=user)

    return render(request,
                  'eventsingle/step1.html',
                  {
                      'user': request.user,

                      'profile': user,
                      'form': form,

                      'show_summary': form.is_valid(),

                      'step': 1
                  })


def step2(request, event_pk):

    return event_register(
        request,
        event_pk,
        template='eventsingle/step2.html',
        extra_context={
            'step': 2
        }
    )


def step3(request, event_pk):

    return eventportal_views.event_status(
        request,
        event_pk,
        template_name='eventsingle/step3.html',
        extra_context={
            'step': 3
        })


def step4(request, event_pk):

    return eventportal_views.event_status(
        request,
        event_pk,
        template_name='eventsingle/step4.html',
        extra_context={
            'step': 4
        })
