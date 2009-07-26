from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.admin.helpers import AdminForm
from django.utils.translation import ugettext as _

from models import Invoice
from forms import InvoiceSourceForm, InvoiceFormattingForm

@staff_member_required
def invoice_report(request,
                   template_name='admin/invoice/invoice/report.html'):

    invoices = []
    line_groups = []

    if request.method == 'POST' or request.GET.has_key('event'):
        sourceform = InvoiceSourceForm(request.REQUEST)

        if sourceform.is_valid():
            invoices = Invoice.objects.all()
            invoices = sourceform.filter(invoices)

            formattingform = InvoiceFormattingForm(request.REQUEST, invoices=invoices)
            if formattingform.is_valid():
                line_groups = formattingform.format(invoices)
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
                               'adminsourceform' : adminsourceform,
                               'adminformattingform' : adminformattingform},
                              context_instance=RequestContext(request))
