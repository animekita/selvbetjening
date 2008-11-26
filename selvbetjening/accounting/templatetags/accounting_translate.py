from django import template
from django.utils.translation import ugettext as _

from selvbetjening.accounting.models import MembershipState

register = template.Library()

@register.filter(name='translate')
def translate(text, category):
    if category == 'membership_state':
        if text == MembershipState.ACTIVE:
            return _('Active member')
        elif text == MembershipState.CONDITIONAL_ACTIVE:
            return _('Conditional active member')
        elif text == MembershipState.PASSIVE:
            return _('Passive member')
        elif text == MembershipState.INACTIVE:
            return _('Inactive member')

    if category == 'membership_state_short':
        if text == MembershipState.ACTIVE:
            return _('Active')
        elif text == MembershipState.CONDITIONAL_ACTIVE:
            return _('Conditional active')
        elif text == MembershipState.PASSIVE:
            return _('Passive')
        elif text == MembershipState.INACTIVE:
            return _('Inactive')

    elif category == 'payment_type':
        if text == 'FULL':
            return _('Full payment')
        elif text == 'FRATE':
            return _('First rate')
        elif text == 'SRATE':
            return _('Second rate')