from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin import helpers
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from forms import PaymentsIntervalForm
from models import Payment

@staff_member_required
def payment_report(request, startdate=None, enddate=None, template_name='admin/accounting/payment/report.html',
                   form_class=PaymentsIntervalForm):

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            startdate = form.cleaned_data['startdate']
            enddate = form.cleaned_data['enddate']
    else:
        form = form_class()

    payments = []
    total = 0

    if startdate is not None and enddate is not None:
        payments = Payment.objects.filter(timestamp__gte=startdate).filter(timestamp__lte=enddate)

        for payment in payments:
            total += payment.get_ammount()

    return render_to_response(template_name,
                              {'adminform' : helpers.AdminForm(form,
                                                               [(None, {'fields': form.base_fields.keys()})],
                                                               {}),
                               'payments' : payments,
                               'total' : total,
                               'startdate' : startdate,
                               'enddate' : enddate},
                              context_instance=RequestContext(request))

