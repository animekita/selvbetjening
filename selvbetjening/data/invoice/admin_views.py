# -- encoding: utf-8 --

from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.admin.helpers import AdminForm
from django.utils.translation import ugettext as _
from django.template.loader import get_template_from_string

if 'mailer' in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
    from django.core.mail import send_mail

from selvbetjening.data.events.models import Attend

from models import Invoice, InvoicePaymentWorkflow, Payment
from forms import InvoiceSourceForm, InvoiceFormattingForm, InvoicePaymentForm

def invoice_select_workflow(request,
                            template_name='admin/invoice/invoice/select_workflow.html'):

    workflows = InvoicePaymentWorkflow.objects.all()

    return render_to_response(template_name,
                              {'workflows': workflows},
                              context_instance=RequestContext(request))

def invoice_pay(request,
                workflow_id,
                payment_form=InvoicePaymentForm,
                template_name='admin/invoice/invoice/workflow.html'):

    workflow = get_object_or_404(InvoicePaymentWorkflow, pk=workflow_id)

    changed_attendee = None
    changed_payment = None

    if request.method == 'POST':
        form = payment_form(request.POST)

        if form.is_valid():
            attendee = Attend.objects.get(invoice=form.invoice)
            payment = Payment.objects.create(revision=form.invoice.latest_revision,
                                             amount=form.payment,
                                             signee=request.user)

            subject = workflow.notification_email_subject
            content = {'invoice_rev' : attendee.invoice.latest_revision,
                       'attendee' : attendee,
                       'payment': payment}

            message_body = get_template_from_string(workflow.notification_email).render(content)

            send_mail(subject, message_body, settings.DEFAULT_FROM_EMAIL, [attendee.user.email,])

            changed_attendee = attendee
            changed_payment = payment

            form = payment_form()

    else:
        form = payment_form()

    adminform = AdminForm(form,
                          [(None, {'fields': form.base_fields.keys()})],
                          {}
                          )

    return render_to_response(template_name, {'form': form,
                                              'adminform' : adminform,
                                              'changed_attendee' : changed_attendee,
                                              'changed_payment' : changed_payment},
                              context_instance=RequestContext(request))

def invoice_report(request,
                   template_name='admin/invoice/invoice/report.html'):

    invoices = []
    line_groups = []
    total = None

    if request.method == 'POST' or request.GET.has_key('event'):
        sourceform = InvoiceSourceForm(request.REQUEST)

        if sourceform.is_valid():
            invoices = sourceform.filter(Invoice.objects)

            formattingform = InvoiceFormattingForm(request.REQUEST, invoices=invoices)
            if formattingform.is_valid():
                line_groups, total = formattingform.format()
        else:
            formattingform = InvoiceFormattingForm(request.REQUEST)
    else:
        sourceform = InvoiceSourceForm()
        formattingform = InvoiceFormattingForm()

    adminsourceform = AdminForm(sourceform,
                                [(_('Source'), {'fields': sourceform.base_fields.keys()})],
                                {})

    adminformattingform = AdminForm(formattingform,
                                    [(_('Formatting'), {'fields': formattingform.base_fields.keys()})],
                                    {})

    return render_to_response(template_name,
                              {'invoices' : invoices,
                               'line_groups' : line_groups,
                               'total' : total,
                               'adminsourceform' : adminsourceform,
                               'adminformattingform' : adminformattingform},
                              context_instance=RequestContext(request))
