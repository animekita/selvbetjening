from datetime import datetime

from django.template.loader import render_to_string
from django.contrib.admin.helpers import AdminForm

from selvbetjening.data.events.models import Attend

from forms import MembershipForm
from membership_controller import MembershipController

def membership(request, user, event):
    def member_status_view():
        return render_to_string('membership/checkin/status.html',
                                {})

    if MembershipController.is_member(user, event=event):
        return (True, member_status_view)

    attend = Attend.objects.get(event=event, user=user)
    
    if request.method == 'POST':
        form = MembershipForm(request.POST, user=user, event=event)
        if form.is_valid():
            form.save(attend.invoice)
            return (True, member_status_view)
    else:
        form = MembershipForm(user=user, event=event)

    def member_payment_view():
        return render_to_string('membership/checkin/payment.html',
                                {'adminform' : AdminForm(form,
                                                         [(None, {'fields': form.base_fields.keys()})],
                                                         {}),
                                 })

    return (False, member_payment_view)