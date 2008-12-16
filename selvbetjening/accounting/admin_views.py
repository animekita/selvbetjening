from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from forms import PaymentsIntervalForm

@staff_member_required
def payment_report(request, startdate=None, enddate=None, template_name='admin/accounting/payment/report.html',
                   form_class=PaymentsIntervalForm):

    payments = []
    total = 0

    if startdate is not None and enddate is not None:
        payments = Payment.objects.filter(timestamp__gte=startdate).filter(timestamp__lte=enddate)

        for payment in payments:
            total += payment.get_ammount()

    form = form_class()

    return render_to_response(template_name,
                              {'form' : form,
                               'payments' : payments,
                               'total' : total,
                               'startdate' : startdate,
                               'enddate' : enddate},
                              context_instance=RequestContext(request))

