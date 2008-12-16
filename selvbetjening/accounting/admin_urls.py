from django.conf.urls.defaults import *

import admin_views

urlpatterns = patterns('',
    url(r'^accounting/payment/report/(?P<startdate>[0-9]{4}\-[0-9]{2}\-[0-9]{2})/(?P<enddate>[0-9]{4}\-[0-9]{2}\-[0-9]{2})/',
        admin_views.payment_report, name='admin_payment_report'),
    url(r'^accounting/payment/report/', admin_views.payment_report, name='admin_payment_report'),
)