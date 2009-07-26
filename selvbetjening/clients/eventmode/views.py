# encoding: utf-8

from django import shortcuts
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.helpers import AdminForm
from django.contrib.auth.models import User

from selvbetjening.data.logging import logger
from selvbetjening.data.logging.decorators import log_access
from selvbetjening.data.events.models import Event, Attend, Option
from selvbetjening.data.invoice.models import Payment

from selvbetjening.data.members.forms import RegistrationForm

from decorators import eventmode_required
import processor_handlers
from forms import PaymentForm

def login(request, template_name='eventmode/login.html',
          success_page='eventmode_list_attendees'):

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
                                request.eventmode.model.event.pk)

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
@log_access
def list_attendees(request,
                   template_name='eventmode/list_attendees.html'):

    event = request.eventmode.model.event

    class DummyModelAdmin:
        ordering = None

        def queryset(self, request):
            return Attend.objects.filter(event=event)

    def actions(attend):
        actions = ''

        actions += u"""
        <a href="%s"><input type="button" value="Ændre tilvalg"/></a>
        """ % reverse('eventmode_change_selections', kwargs={'user_id': attend.user.pk})

        actions += u"""
        <a href="%s"><input type="button" value="Billing"/></a>
        """ % reverse('eventmode_billing', kwargs={'user_id': attend.user.pk})

        if not attend.has_attended:
            actions += u"""
            <a href="%s"><input style="font-weight: bold;" type="button" value="Checkin"/></a>
            """ % reverse('eventmode_checkin', kwargs={'user_id': attend.user.pk})
        else:
            actions += u"""
            <a href="%s"><input type="button" value="Checkout"/></a>
            """ % reverse('eventmode_checkout', kwargs={'user_id': attend.user.pk})


        return actions
    actions.allow_tags = True
    actions.short_description = _('Actions')

    def has_paid(attend):
        return attend.invoice.is_paid()
    has_paid.boolean = True

    cl = ChangeList(request,
                    Attend,
                    ('user', 'user_first_name', 'user_last_name', 'has_attended', 'is_new', has_paid, actions),
                    ('username',),
                    ('has_attended',),
                    (),
                    ('user__username', 'user__first_name', 'user__last_name'),
                    (),
                    50,
                    (),
                    DummyModelAdmin())
    cl.formset = None

    return render_to_response(template_name,
                              {'attendees' : event.attendees,
                               'results' : event.attendees,
                               'event' : event,
                               'cl' : cl},
                              context_instance=RequestContext(request))

@eventmode_required
@log_access
def billing(request,
            user_id,
            template_name='eventmode/billing.html'):

    event = request.eventmode.model.event
    attendee = shortcuts.get_object_or_404(Attend, event=event, user=user_id)

    payment = Payment(revision=attendee.invoice.latest_revision,
                      amount=attendee.invoice.unpaid,
                      note=_('Paid at %(event)s') % {'event' : event.title})

    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)

        if form.is_valid():
            form.save()

        return HttpResponseRedirect(reverse('eventmode_billing', kwargs={'user_id' : user_id}))

    else:
        form = PaymentForm(instance=payment)

    adminform = AdminForm(form,
                          [(None, {'fields': form.base_fields.keys()})],
                          {}
                          )

    return render_to_response(template_name,
                          {'event' : event,
                           'attendee' : attendee,
                           'adminform' : adminform,
                          },
                          context_instance=RequestContext(request))


@eventmode_required
@log_access
def checkout(request,
            user_id,
            template_name='eventmode/checkout.html'):

    event = request.eventmode.model.event
    attendee = shortcuts.get_object_or_404(Attend, event=event, user=user_id)

    if not attendee.has_attended:
        return HttpResponseRedirect(reverse('eventmode_list_attendees'))

    if request.method == 'POST':
        attendee.has_attended = False
        attendee.save()

        return HttpResponseRedirect(reverse('eventmode_list_attendees'))

    return render_to_response(template_name,
                              {'event' : event,
                               'attendee' : attendee},
                              context_instance=RequestContext(request))

@eventmode_required
@log_access
def checkin(request,
            user_id,
            template_name='eventmode/checkin.html'):

    event = request.eventmode.model.event
    attendee = shortcuts.get_object_or_404(Attend, event=event, user=user_id)

    if attendee.has_attended:
        return HttpResponseRedirect(reverse('eventmode_list_attendees'))

    if request.method == 'POST':
        if request.POST.has_key('do_checkin_and_pay') and not attendee.invoice.in_balance():
            Payment.objects.create(revision=attendee.invoice.latest_revision,
                                   amount=attendee.invoice.unpaid,
                                   note=_('Payment at %(event)s checkin') % {'event' : attendee.event})

        attendee.has_attended = True
        attendee.save()

        return HttpResponseRedirect(reverse('eventmode_list_attendees'))

    submit_allowed, view_functions, save_functions = \
                  processor_handlers.checkin.run_processors(request, attendee)

    checkin_rendered = ''
    for view_func in view_functions:
        checkin_rendered += view_func()

    return render_to_response(template_name,
                              {'event' : event,
                               'attendee' : attendee,
                               'checkin_rendered': checkin_rendered},
                              context_instance=RequestContext(request))

@eventmode_required
@log_access
def change_selections(request, user_id,
                      template_name='eventmode/change_selections.html'):

    event = request.eventmode.model.event
    attendee = shortcuts.get_object_or_404(Attend, event=event, user=user_id)

    checkin_allowed, render_functions, save_functions = \
                   processor_handlers.change_selections.run_processors(request, attendee)

    if request.method == 'POST':
        if checkin_allowed:
            for save_func in save_functions:
                save_func()

            if request.POST.has_key('do_save_and_list'):
                return HttpResponseRedirect(reverse('eventmode_list_attendees'))
            elif request.POST.has_key('do_save_and_checkin'):
                return HttpResponseRedirect(reverse('eventmode_checkin', kwargs={'user_id' : attendee.user.id}))

    checkin_parts = u''
    for render_func in render_functions:
        checkin_parts += render_func()

    return render_to_response(template_name,
                              {'event' : event,
                               'attendee' : attendee,
                               'checkin_parts' : checkin_parts},
                              context_instance=RequestContext(request))



@eventmode_required
@log_access
def add_user(request,
             template_name='eventmode/add_user.html'):

    event = request.eventmode.model.event

    if request.method == 'POST':
        user_id = request.POST.get('add_user', None)

        if user_id is not None:
            user = get_object_or_404(User, pk=user_id)
            event.add_attendee(user)

            return HttpResponseRedirect(reverse('eventmode_change_selections',
                                                kwargs={'user_id' : user.id}))

    class DummyModelAdmin:
        ordering = None

        def queryset(self, request):
            return User.objects.all().exclude(attend__event=event)

    def actions(user):
        actions = ''

        actions += u"""
        <form method="POST" action="">
        <input type="hidden" name="add_user" value="%s" />
        <input type="submit" name="do_add_user" value="Tilføj til event"/>
        </form>
        """ % user.pk

        return actions
    actions.allow_tags = True
    actions.short_description = _('Actions')

    cl = ChangeList(request,
                    User,
                    ('username', 'first_name', 'last_name', actions),
                    ('username',),
                    (),
                    (),
                    ('username', 'first_name', 'last_name'),
                    (),
                    50,
                    (),
                    DummyModelAdmin())
    cl.formset = None

    return render_to_response(template_name,
                              {'event' : event,
                               'cl' : cl},
                              context_instance=RequestContext(request))

@eventmode_required
@log_access
def create_user(request,
                template_name='eventmode/create_user.html'):

    event = request.eventmode.model.event

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            event.add_attendee(user)

            return HttpResponseRedirect(reverse('eventmode_change_selections',
                                                kwargs={'user_id' : user.id}))

    else:
        form = RegistrationForm()

    adminform = AdminForm(form,
                          [(None, {'fields': form.base_fields.keys()})],
                          {}
                          )

    return render_to_response(template_name,
                              {'adminform': adminform},
                              context_instance=RequestContext(request))

