# -- encoding: utf-8 --

from django import shortcuts
from django.utils.translation import gettext as _
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.helpers import AdminForm
from django.contrib.auth.models import User

from selvbetjening.data.invoice.models import Invoice, Payment
from selvbetjening.data.members.forms import RegistrationForm

import processor_handlers
from models import Event, Attend, AttendState
from forms import PaymentForm

def event_statistics(request, event_id, template_name='admin/events/event/statistics.html'):
    event = get_object_or_404(Event, id=event_id)

    checkedin_count = event.attendees.filter(state=AttendState.attended).count()
    attendees_count = event.attendees.count()

    checkedin_precentage = 0
    if event.attendees_count > 0:
        checkedin_precentage = 100 * float(checkedin_count) / float(attendees_count)

    new = 0
    new_checkedin = 0
    for attendee in event.attendees:
        if attendee.is_new():
            new += 1

            if attendee.state == AttendState.attended:
                new_checkedin += 1

    new_checkedin_precentage = 0

    if checkedin_count > 0:
        new_checkedin_precentage = 100 * float(new_checkedin) / float(checkedin_count)

    new_precentage = 0
    if event.attendees_count > 0:
        new_precentage = 100 * float(new) / float(attendees_count)

    total = 0
    paid = 0
    paid_invoices = 0
    number_invoices = 0
    for invoice in Invoice.objects.filter(attend__in=event.attendees):
        number_invoices += 1

        if invoice.is_paid():
            paid_invoices += 1

        total += invoice.total_price
        paid += invoice.paid

    return render_to_response(template_name,
                              {'event' : event,
                               'checkedin_count' : checkedin_count,
                               'attendees_count' : attendees_count,
                               'checkin_precentage' : checkedin_precentage,
                               'new_attendees' : new,
                               'new_checkedin' : new_checkedin,
                               'new_attendees_precentage' : new_precentage,
                               'new_checkedin_precentage' : new_checkedin_precentage,
                               'invoice_total' : total,
                               'invoice_paid' : paid,
                               'number_invoices' : number_invoices,
                               'paid_invoices' : paid_invoices},
                              context_instance=RequestContext(request))

def change_selections(request, attend_id,
                      template_name='admin/events/attend/change_selections.html'):

    attendee = shortcuts.get_object_or_404(Attend, pk=attend_id)
    event = attendee.event


    checkin_allowed, render_functions, save_functions = \
                   processor_handlers.change_selections.run_processors(request, attendee)

    if request.method == 'POST':
        if checkin_allowed:
            for save_func in save_functions:
                save_func()

            if request.POST.has_key('do_save_and_list'):
                return HttpResponseRedirect(reverse('admin:events_attend_changelist'))
            elif request.POST.has_key('do_save_and_checkin'):
                return HttpResponseRedirect(reverse('admin:events_attend_checkin', args=[attendee.pk]))

    checkin_parts = u''
    for render_func in render_functions:
        checkin_parts += render_func()

    return render_to_response(template_name,
                              {'event' : event,
                               'attendee' : attendee,
                               'checkin_parts' : checkin_parts},
                              context_instance=RequestContext(request))

def billing(request, attend_id,
            template_name='admin/events/attend/billing.html'):

    attendee = shortcuts.get_object_or_404(Attend, pk=attend_id)
    event = attendee.event

    payment = Payment(revision=attendee.invoice.latest_revision,
                      amount=attendee.invoice.unpaid,
                      note=_('Paid at %(event)s') % {'event' : event.title})

    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)

        if form.is_valid():
            form.save()

        return HttpResponseRedirect(reverse('admin:events_attend_billing', args=[attendee.pk]))

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

def checkout(request,
            attend_id,
            template_name='admin/events/attend/checkout.html'):

    attendee = shortcuts.get_object_or_404(Attend, pk=attend_id)
    event = attendee.event

    if not attendee.state == AttendState.attended:
        return HttpResponseRedirect(reverse('admin:events_attend_changelist'))

    if request.method == 'POST':
        attendee.state = AttendState.accepted
        attendee.save()

        return HttpResponseRedirect(reverse('admin:events_attend_changelist'))

    return render_to_response(template_name,
                              {'event' : event,
                               'attendee' : attendee},
                              context_instance=RequestContext(request))

def checkin(request, attend_id,
            template_name='admin/events/attend/checkin.html'):

    attendee = shortcuts.get_object_or_404(Attend, pk=attend_id)
    event = attendee.event

    if attendee.state == AttendState.attended:
        return HttpResponseRedirect(reverse('admin:events_attend_changelist'))

    if request.method == 'POST':
        if request.POST.has_key('do_checkin_and_pay') and not attendee.invoice.in_balance():
            Payment.objects.create(revision=attendee.invoice.latest_revision,
                                   amount=attendee.invoice.unpaid,
                                   note=_('Payment at %(event)s checkin') % {'event' : attendee.event})

        attendee.state = AttendState.attended
        attendee.save()

        return HttpResponseRedirect(reverse('admin:events_attend_changelist'))

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

def add_user(request, event_id,
             template_name='admin/events/attend/add_user.html'):

    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'POST':
        user_id = request.POST.get('add_user', None)

        if user_id is not None:
            user = get_object_or_404(User, pk=user_id)
            attendee = event.add_attendee(user)

            return HttpResponseRedirect(reverse('admin:events_attend_selections_change',
                                                args=[attendee.pk]))

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
