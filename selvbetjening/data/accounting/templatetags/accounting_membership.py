from django import template
from django.utils.translation import ugettext as _

from selvbetjening.data.accounting.models import Payment

import accounting_translate

register = template.Library()

@register.filter(name='membership_state')
def membership_state(user):
    state = Payment.objects.get_membership_state(user)
    return accounting_translate.translate(state, 'membership_state')