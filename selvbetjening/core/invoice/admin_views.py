# -- encoding: utf-8 --

from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.admin.helpers import AdminForm
from django.utils.translation import ugettext as _
from django.template.loader import get_template_from_string
from django.template import Context
from django.core.exceptions import PermissionDenied

if 'mailer' in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
    from django.core.mail import send_mail

from selvbetjening.core.events.models import Attend

from models import Invoice, InvoicePaymentWorkflow, Payment
from forms import InvoiceSourceForm, InvoiceFormattingForm, InvoicePaymentForm

def invoice_select_workflow(request,
                            model_admin,
                            template_name='admin/invoice/invoice/select_workflow.html'):

    if not model_admin.has_change_permission(request, None):
        raise PermissionDenied

    workflows = InvoicePaymentWorkflow.objects.all()

    return render_to_response(template_name,
                              {'workflows': workflows},
                              context_instance=RequestContext(request))

def invoice_report(request,
                   model_admin,
                   template_name='admin/invoice/invoice/report.html'):

    if not model_admin.has_change_permission(request, None):
        raise PermissionDenied

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
