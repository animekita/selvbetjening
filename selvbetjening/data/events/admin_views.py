from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from selvbetjening.data.invoice.models import Invoice

from models import Event

@staff_member_required
def event_statistics(request, event_id, template_name='admin/events/event/statistics.html'):
    event = get_object_or_404(Event, id=event_id)

    checkedin_precentage = 0
    if event.attendees_count > 0:
        checkedin_precentage = 100 * float(event.checkedin_count) / float(event.attendees_count)

    new = 0
    new_checkedin = 0
    for attendee in event.attendees:
        if attendee.is_new():
            new += 1

            if attendee.has_attended:
                new_checkedin += 1

    new_checkedin_precentage = 0
    if event.checkedin_count > 0:
        new_checkedin_precentage = 100 * float(new_checkedin) / float(event.checkedin_count)

    new_precentage = 0
    if event.attendees_count > 0:
        new_precentage = 100 * float(new) / float(event.attendees_count)

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

@staff_member_required
def event_options_print(request,
                        event_id,
                        template_name='admin/events/event/options_print.html'):

    event = get_object_or_404(Event, id=event_id)

    return render_to_response(template_name,
                              {'event' : event},
                              context_instance=RequestContext(request))
