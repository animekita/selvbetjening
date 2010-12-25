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

from selvbetjening.core.invoice.models import Invoice, Payment
from selvbetjening.core.members.forms import RegistrationForm

from processor_handlers import change_selection_processors, checkin_processors
from models import Event, Attend, AttendState
from forms import PaymentForm

def event_statistics(request, event_id, template_name='admin/events/event/statistics.html'):
    statistics = {}

    event = get_object_or_404(Event, id=event_id)

    # attendees
    attendees_count = event.attendees.count()

    def attendee_statistics(state, identifier):
        attendees = event.attendees.filter(state=state)
        count = attendees.count()

        new = 0
        for attendee in attendees:
            if attendee.is_new():
                new += 1

        statistics[identifier + '_count'] = count
        statistics[identifier + '_new'] = new

        return new

    new_count = attendee_statistics(AttendState.waiting, 'waiting')
    new_count += attendee_statistics(AttendState.accepted, 'accepted')
    new_count += attendee_statistics(AttendState.attended, 'attended')

    # invoices
    statistics['invoice_payment_total'] = 0
    statistics['invoice_paid'] = 0

    statistics['invoices_in_balance'] = 0
    statistics['invoices_unpaid'] = 0
    statistics['invoices_partial'] = 0
    statistics['invoices_overpaid'] = 0
    statistics['invoices_count'] = 0

    for invoice in Invoice.objects.filter(attend__in=event.attendees):
        statistics['invoices_count'] += 1

        if invoice.in_balance():
            statistics['invoices_in_balance'] += 1

        if invoice.is_unpaid():
            statistics['invoices_unpaid'] += 1

        if invoice.is_overpaid():
            statistics['invoices_overpaid'] += 1

        if invoice.is_partial():
            statistics['invoices_partial'] += 1

        statistics['invoice_payment_total'] += invoice.total_price
        statistics['invoice_paid'] += invoice.paid

    # tilvalg

    optiongroups = []
    for optiongroup in event.optiongroup_set.all():
        options = []
        for option in optiongroup.option_set.all():
            count = option.selections.count()
            waiting = option.selections.filter(attendee__state=AttendState.waiting).count()
            accepted = option.selections.filter(attendee__state=AttendState.accepted).count()
            attended = option.selections.filter(attendee__state=AttendState.attended).count()
            options.append((option, count, waiting, accepted, attended))

        optiongroups.append((optiongroup, options))

    statistics.update({'event' : event,
                       'attendees_count' : attendees_count,
                       'new_count' : new_count,
                       'optiongroups' : optiongroups,})

    return render_to_response(template_name,
                              statistics,
                              context_instance=RequestContext(request))

def change_selections(request, attend_id,
                      template_name='admin/events/attend/change_selections.html'):

    attendee = shortcuts.get_object_or_404(Attend, pk=attend_id)
    event = attendee.event

    handler = change_selection_processors.get_handler(request, attendee)

    if request.method == 'POST':
        if handler.is_valid():
            handler.save()

            if request.POST.has_key('do_save_and_list'):
                return HttpResponseRedirect(reverse('admin:events_attend_changelist'))
            elif request.POST.has_key('do_save_and_checkin'):
                return HttpResponseRedirect(reverse('admin:events_attend_checkin', args=[attendee.pk]))

    checkin_parts = handler.view()

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

def get_checkin_list_url(attendee):
    return reverse('admin:events_attend_changelist') + '?event__id__exact=%s' % attendee.event.pk

def checkout(request,
            attend_id,
            template_name='admin/events/attend/checkout.html'):

    attendee = shortcuts.get_object_or_404(Attend, pk=attend_id)
    event = attendee.event

    if not attendee.state == AttendState.attended:
        return HttpResponseRedirect(get_checkin_list_url(attendee))

    if request.method == 'POST':
        attendee.state = AttendState.accepted
        attendee.save()

        request.user.message_set.create(message=u'%s checked out for event %s' % (attendee.user, attendee.event))

        return HttpResponseRedirect(get_checkin_list_url(attendee))

    return render_to_response(template_name,
                              {'event' : event,
                               'attendee' : attendee},
                              context_instance=RequestContext(request))

def checkin(request, attend_id,
            template_name='admin/events/attend/checkin.html'):

    attendee = shortcuts.get_object_or_404(Attend, pk=attend_id)
    event = attendee.event

    if attendee.state == AttendState.attended:
        return HttpResponseRedirect(get_checkin_list_url(attendee))

    if request.method == 'POST':
        if request.POST.has_key('do_checkin_and_pay') and not attendee.invoice.in_balance():
            Payment.objects.create(revision=attendee.invoice.latest_revision,
                                   amount=attendee.invoice.unpaid,
                                   note=_('Payment at %(event)s checkin') % {'event' : attendee.event})

        attendee.state = AttendState.attended
        attendee.save()

        request.user.message_set.create(message=u'%s checked in for event %s' % (attendee.user, attendee.event))

        return HttpResponseRedirect(get_checkin_list_url(attendee))

    handler = checkin_processors.get_handler(request, attendee)

    checkin_rendered = handler.view()

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