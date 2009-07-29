from django.conf.urls.defaults import url, patterns

import admin_views

urlpatterns = patterns(
    '',
    url(r'^invoice/invoice/report/$',
        admin_views.invoice_report,
        name='invoice_report'),
    url(r'^invoice/invoice/goto/$',
        admin_views.invoice_goto,
        name='invoice_goto'),
)