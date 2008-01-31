from datetime import date

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import ugettext as _
from django import oldforms
from django.contrib.auth.models import User
from django import shortcuts
from django.http import HttpResponseRedirect

import forms
from models import Payment

@permission_required('accounting.add_payment')
def payment_history(request, user, template_name='accounting/history.html'):
    userobj = shortcuts.get_object_or_404(User, username=user)
    return render_to_response(template_name,
                              {'payments' : userobj.payment_set.all(), 'username' : user},
                              context_instance=RequestContext(request))

@permission_required('accounting.add_payment')
def pay(request, user, template_name='accounting/pay.html', success_page='accounting_list'):
    userobj = shortcuts.get_object_or_404(User, username=user)

    if userobj.get_profile().get_membership_state() == 'ACTIVE':
        return render_to_response(template_name,
                                  {'no_options' : True},
                                  context_instance=RequestContext(request))

    if request.method == 'POST':
        form = forms.PaymentForm(request.POST, user=userobj)
        if form.is_valid():
            form.save()
            request.user.message_set.create(message=_(u'Payment noted'))
            return HttpResponseRedirect(reverse(success_page))
    else:
        form = forms.PaymentForm(user=userobj)

    return render_to_response(template_name,
                              {'form' : form, 'username' : user},
                              context_instance=RequestContext(request))

@permission_required('accounting.add_payment')
def list(request, template_name='accounting/list.html'):
    return render_to_response(template_name,
                              {'users' : User.objects.all()},
                              context_instance=RequestContext(request))

@permission_required('accounting.add_payment')
def payments(request, template_name='accounting/payments.html', 
             form_class=forms.PaymentsIntervalForm):

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('accounting_payments_detail', kwargs={'startdate' : form.cleaned_data['startdate'], 'enddate' : form.cleaned_data['enddate']}))
    else:
        form = form_class()
        
    return render_to_response(template_name,
                              {'form' : form},
                              context_instance=RequestContext(request))

@permission_required('accounting.add_payment')
def payments_detail(request, startdate, enddate, 
                    template_name='accounting/payments_detail.html'):

    payments = Payment.objects.filter(timestamp__gte=startdate).filter(timestamp__lte=enddate)
    
    total = 0
    for payment in payments:
        total += payment.get_ammount()
    
    return render_to_response(template_name,
                              {'payments' : payments, 'total' : total, 'startdate' : startdate, 'enddate' : enddate},
                              context_instance=RequestContext(request))
