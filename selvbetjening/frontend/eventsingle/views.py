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
from django.contrib import messages
from django.utils.translation import ugettext as _

from selvbetjening.core.events.options.dynamic_selections import dynamic_selections_formset_factory
from selvbetjening.core.events.options.scope import SCOPE

from selvbetjening.core.user.models import SUser
from selvbetjening.frontend.base.views.events import generic_event_status
from selvbetjening.frontend.eventportal.views import event_register

from selvbetjening.core.events.models import Attend, AttendState

from selvbetjening.businesslogic.events import decorators as eventdecorators
from selvbetjening.businesslogic.members.forms import MinimalUserRegistrationForm, ProfileEditForm
from selvbetjening.businesslogic.events.decorators import event_registration_open_required, \
    get_event_from_id, suspend_automatic_attendee_price_updates

from selvbetjening.frontend.auth.forms import AuthenticationForm
from selvbetjening.frontend.eventportal import views as eventportal_views
from selvbetjening.sadmin2.forms import attendee_selection_helper_factory


def _get_step(request, event_pk):
    # step 0 - user not logged in
    if not request.user.is_authenticated():
        return 0, False, False

    # step 1 or 2 - user not attending event
    try:
        attendee = Attend.objects.get(user=request.user, event__pk=event_pk)
    except Attend.DoesNotExist:

        # step 1 - verify user data
        if not request.session.get('user-data-verified', False):
            return 1, True, False

        return 2, True, True

    # step 3 - user not accepted
    if attendee.state == AttendState.waiting:
        return 3, True, True

    # step 4
    return 4, False, False


def step_controller(request,
                    event_pk,
                    step1_form=None):

    step, edit_profile, edit_selections = _get_step(request, event_pk)

    if step == 0:
        return step0(request, event_pk)

    if step == 1:
        return step1(request, event_pk,
                     form_class=step1_form)

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

                      'step': 0,
                      'can_edit_profile': False,
                      'can_edit_selections': False
                  })


@get_event_from_id
@event_registration_open_required
@suspend_automatic_attendee_price_updates
@login_required
def step1(request,
          event,
          form_class=None,
          skip_summary=False,
          update_mode=False):

    if form_class is None:
        form_class = ProfileEditForm

    user = request.user

    if request.method == 'POST':
        form = form_class(request.POST, instance=user)

        if form.is_valid():
            form.save()

            request.session['user-data-verified'] = True
            messages.success(request, _('Profile updated'))

            return HttpResponseRedirect(reverse('eventsingle_steps', kwargs={'event_pk': event.pk}))

    else:
        form = form_class(instance=user)

    step, edit_profile, edit_selections = _get_step(request, event.pk)

    return render(request,
                  'eventsingle/step1.html',
                  {
                      'user': request.user,

                      'profile': user,
                      'form': form,

                      'show_summary': form.is_valid() and not skip_summary,
                      'update_mode': update_mode,

                      'step': step,
                      'can_edit_profile': edit_profile,
                      'can_edit_selections': edit_selections
                  })


@login_required
@eventdecorators.get_event_from_id
@eventdecorators.event_registration_open_required
@suspend_automatic_attendee_price_updates
def step2(request, event):

    EventSelectionFormSet = dynamic_selections_formset_factory(
        SCOPE.EDIT_REGISTRATION,
        event,
        helper_factory=attendee_selection_helper_factory
    )

    try:
        attendee = Attend.objects.get(event=event, user=request.user)
        instance_kwargs = {'instance': attendee}
    except Attend.DoesNotExist:
        attendee = None
        instance_kwargs = {}

    if request.method == 'POST':
        options_form = EventSelectionFormSet(request.POST, **instance_kwargs)

        if options_form.is_valid():

            if attendee is None:
                attendee = Attend.objects.create(event=event, user=request.user, price=0)
            else:
                messages.success(request, _('Selections updated'))

            options_form.save(attendee=attendee)

            attendee.recalculate_price()
            attendee.event.send_notification_on_registration(attendee)

            return HttpResponseRedirect(
                reverse('eventsingle_steps', kwargs={'event_pk': event.pk})
            )

    else:
        options_form = EventSelectionFormSet(**instance_kwargs)

    step, edit_profile, edit_selections = _get_step(request, event.pk)

    return render(request,
                  'eventsingle/step2.html',
                  {
                      'formset': options_form,

                      'step': step,
                      'can_edit_profile': edit_profile,
                      'can_edit_selections': edit_selections
                  })


@login_required
@eventdecorators.get_event_from_id
@eventdecorators.event_attendance_required
def step3(request, event):

    step, edit_profile, edit_selections = _get_step(request, event.pk)

    return generic_event_status(
        request,
        event,
        template_name='eventsingle/step3.html',
        extra_context={
            'step': step,
            'can_edit_profile': edit_profile,
            'can_edit_selections': edit_selections
        })


@login_required
@eventdecorators.get_event_from_id
@eventdecorators.event_attendance_required
def step4(request, event):

    return generic_event_status(
        request,
        event,
        template_name='eventsingle/step4.html',
        extra_context={
            'step': 4,
            'can_edit_profile': False,
            'can_edit_selections': False
        })
