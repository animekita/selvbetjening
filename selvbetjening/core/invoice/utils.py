
def sum_invoices(invoices):

    # Initialize base values for all totals
    total = {'potential': 0, 'potential_total': 0,
             'overpaid': 0, 'overpaid_total': 0,
             'underpaid': 0, 'underpaid_total': 0,
             'unpaid': 0, 'unpaid_total': 0,
             'realised': 0, 'realised_total': 0}

    for invoice in invoices:

        total['potential_total'] += invoice.total_price
        total['potential'] += 1

        if invoice.is_overpaid():
            total['overpaid_total'] += invoice.overpaid
            total['overpaid'] += 1

        elif invoice.is_partial():
            total['underpaid_total'] += invoice.unpaid
            total['underpaid'] += 1

        elif invoice.is_unpaid():
            total['unpaid_total'] += invoice.unpaid
            total['unpaid'] += 1

        total['realised_total'] += invoice.paid
        total['realised'] += 1 if not invoice.is_unpaid() else 0

    return total