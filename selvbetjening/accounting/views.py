from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from selvbetjening.core.decorators import log_access
from selvbetjening.core import logger

from forms import PaymentForm, PaymentsIntervalForm
from models import Payment

@permission_required('accounting.add_payment')
@log_access
def pay(request, user, template_name='accounting/pay.html', success_page='accounting_list'):
    userobj = get_object_or_404(User, username=user)

    if userobj.get_profile().get_membership_state() == 'ACTIVE':
        return render_to_response(template_name,
                                  {'no_options' : True},
                                  context_instance=RequestContext(request))

    if request.method == 'POST':
        form = PaymentForm(request.POST, user=userobj)
        if form.is_valid():
            form.save()
            logger.info(request, 'client registered payment for user_id %s' % userobj.id)
            request.user.message_set.create(message=_(u'Payment noted'))
            return HttpResponseRedirect(reverse(success_page))
    else:
        form = PaymentForm(user=userobj)

    return render_to_response(template_name,
                              {'form' : form, 'username' : user},
                              context_instance=RequestContext(request))
