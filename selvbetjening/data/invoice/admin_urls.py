from django.conf.urls.defaults import url, patterns

import admin_views

urlpatterns = patterns(
    '',
    url(r'^invoice/invoice/report/$',
        admin_views.invoice_report,
        name='invoice_report'),
)