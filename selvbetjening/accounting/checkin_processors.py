#
#def membership_checking_processor(request):
#    return (allow_checkin, render_func)
from datetime import datetime

from django.template.loader import render_to_string
from django.contrib.admin.helpers import AdminForm

from models import Payment, MembershipState
from forms import PaymentForm

def membership(request, user, event):
    membership_state = Payment.objects.get_membership_state(user)

    def member_status_view():
        return render_to_string('accounting/checkin/status.html',
                                {'membership_state' : membership_state, })

    # Fix: If membership were set to conditional active
    # right now, then act like it is active
    if membership_state == MembershipState.CONDITIONAL_ACTIVE:
        if Payment.objects.member_since(user).date() == datetime.today().date():
            membership_state = MembershipState.ACTIVE

    if membership_state == MembershipState.ACTIVE:
        return (True, member_status_view)

    if request.method == 'POST':
        form = PaymentForm(request.POST, user=user)
        if form.is_valid():
            form.save()
            return (True, member_status_view)
    else:
        form = PaymentForm(user=user)

    def member_payment_view():
        return render_to_string('accounting/checkin/payment.html',
                                {'adminform' : AdminForm(form,
                                                         [(None, {'fields': form.base_fields.keys()})],
                                                         {}),
                                 'membership_state' : membership_state,})

    return (False, member_payment_view)