
def sum_attendee_payment_status(attendees):

    # Initialize base values for all totals
    total = {'potential': 0, 'potential_total': 0,
             'overpaid': 0, 'overpaid_total': 0,
             'underpaid': 0, 'underpaid_total': 0,
             'unpaid': 0, 'unpaid_total': 0,
             'realised': 0, 'realised_total': 0}

    for attendee in attendees:

        total['potential_total'] += attendee.price
        total['potential'] += 1

        if attendee.is_overpaid():
            total['overpaid_total'] += attendee.overpaid
            total['overpaid'] += 1

        elif attendee.is_partial():
            total['underpaid_total'] += attendee.unpaid
            total['underpaid'] += 1

        elif attendee.is_unpaid():
            total['unpaid_total'] += attendee.unpaid
            total['unpaid'] += 1

        total['realised_total'] += attendee.paid
        total['realised'] += 1 if not attendee.is_unpaid() else 0

    return total
