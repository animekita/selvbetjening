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
from django.contrib.auth import login, authenticate, REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import is_safe_url
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_page

from selvbetjening.core.events.options.dynamic_selections import dynamic_selections_formset_factory
from selvbetjening.core.events.options.scope import SCOPE
from selvbetjening.core.events.signals import attendee_updated_signal

from selvbetjening.frontend.base.forms import frontend_selection_helper_factory
from selvbetjening.frontend.base.views.events import generic_event_status

from selvbetjening.core.events.models import Attend, AttendState, AttendeeAcceptPolicy

from selvbetjening.businesslogic.events import decorators as eventdecorators
from selvbetjening.businesslogic.members.forms import MinimalUserRegistrationForm, ProfileEditForm
from selvbetjening.businesslogic.events.decorators import event_registration_open_required, \
    get_event_from_id, suspend_automatic_attendee_price_updates

from selvbetjening.frontend.auth.forms import AuthenticationForm


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
                    step1_form=None,
                    step0_template=None,
                    step1_template=None,
                    step2_template=None,
                    step3_template=None,
                    step4_template=None):

    step, edit_profile, edit_selections = _get_step(request, event_pk)

    if step == 0:
        return step0(request,
                     event_pk,
                     template=step0_template)

    if step == 1:
        return step1(request, event_pk,
                     form_class=step1_form,
                     template=step1_template)

    elif step == 2:
        return step2(request, event_pk, template=step2_template)

    elif step == 3:
        return step3(request, event_pk, template=step3_template)

    return step4(request, event_pk, template=step4_template)


@get_event_from_id
@event_registration_open_required
@suspend_automatic_attendee_price_updates
def step0(request,
          event,
          template=None):
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

            redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')

            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = reverse('eventsingle_steps', kwargs={'event_pk': event.pk})

            return HttpResponseRedirect(redirect_to)

    else:
        login_form = AuthenticationForm()

    return render(request,
                  template if template is not None else 'eventsingle/step0.html',
                  {
                      'event': event,

                      'authentication_form': login_form,
                      'registration_form': registration_form,

                      'handle_authentication': handle_login,
                      'handle_registration': handle_registration,

                      'step': 0,
                      'current_step': 0,
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
          update_mode=False,
          template=None):

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
                  template if template is not None else 'eventsingle/step1.html',
                  {
                      'user': request.user,

                      'profile': user,
                      'form': form,

                      'show_summary': form.is_valid() and not skip_summary,
                      'update_mode': update_mode,

                      'step': step,
                      'current_step': 1,
                      'can_edit_profile': edit_profile,
                      'can_edit_selections': edit_selections
                  })


@eventdecorators.get_event_from_id
@eventdecorators.event_registration_open_required
@suspend_automatic_attendee_price_updates
@login_required
def step2(request,
          event,
          template=None):

    # TODO This method should be merged with the nearly identical registration method in eventportal

    step, edit_profile, edit_selections = _get_step(request, event.pk)

    if step < 2:
        # we have not arrived at this step yet
        return HttpResponseRedirect(
            reverse('eventsingle_steps', kwargs={'event_pk': event.pk})
        )

    try:
        attendee = Attend.objects.get(event=event, user=request.user)
        instance_kwargs = {
            'instance': attendee,
            'user': request.user
        }

        if attendee.state == AttendState.waiting:
            scope = SCOPE.EDIT_MANAGE_WAITING
        elif attendee.state == AttendState.accepted:
            scope = SCOPE.EDIT_MANAGE_ACCEPTED
        else:
            scope = SCOPE.EDIT_MANAGE_ATTENDED

    except Attend.DoesNotExist:
        attendee = None
        instance_kwargs = {
            'user': request.user
        }

        scope = SCOPE.EDIT_REGISTRATION

    EventSelectionFormSet = dynamic_selections_formset_factory(
        scope,
        event,
        helper_factory=frontend_selection_helper_factory
    )

    if request.method == 'POST':
        options_form = EventSelectionFormSet(request.POST, **instance_kwargs)

        if options_form.is_valid():

            if attendee is None:
                attendee = Attend.objects.create(event=event, user=request.user, price=0)
            else:
                messages.success(request, _('Selections updated'))

            options_form.save(attendee=attendee)

            attendee.recalculate_price()

            # If the user has paid fully, and the event policy is to move paid members to the attended state, then do it
            if event.move_to_accepted_policy == AttendeeAcceptPolicy.on_payment and attendee.is_paid():
                attendee.state = AttendState.accepted
                attendee.save()

            if scope == SCOPE.EDIT_REGISTRATION:
                attendee.event.send_notification_on_registration(attendee)
            else:
                attendee.event.send_notification_on_registration_update(attendee)

            attendee_updated_signal.send(step2, attendee=attendee)

            return HttpResponseRedirect(
                reverse('eventsingle_steps', kwargs={'event_pk': event.pk})
            )

    else:
        options_form = EventSelectionFormSet(**instance_kwargs)

    return render(request,
                  template if template is not None else 'eventsingle/step2.html',
                  {
                      'formset': options_form,

                      'step': step,
                      'current_step': 2,
                      'can_edit_profile': edit_profile,
                      'can_edit_selections': edit_selections,
                      'edit_mode': step > 2
                  })


@login_required
@eventdecorators.get_event_from_id
@eventdecorators.event_attendance_required
def step3(request,
          event,
          template=None):

    step, edit_profile, edit_selections = _get_step(request, event.pk)

    return generic_event_status(
        request,
        event,
        template_name=template if template is not None else 'eventsingle/step3.html',
        extra_context={
            'step': step,
            'current_step': 3,
            'can_edit_profile': edit_profile,
            'can_edit_selections': edit_selections
        })


@login_required
@eventdecorators.get_event_from_id
@eventdecorators.event_attendance_required
def step4(request,
          event,
          template=None):

    return generic_event_status(
        request,
        event,
        template_name=template if template is not None else 'eventsingle/step4.html',
        extra_context={
            'step': 4,
            'current_step': 4,
            'can_edit_profile': False,
            'can_edit_selections': False
        })
