from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    url(r'^bruger/(?P<user>.+)/historie/', views.payment_history, name='accounting_history'),
    url(r'^bruger/(?P<user>.+)/betal/', views.pay, name='accounting_pay'),
    url(r'^list/', views.list, name='accounting_list'),
    url(r'^betalinger/(?P<startdate>[0-9]{4}\-[0-9]{2}\-[0-9]{2})/(?P<enddate>[0-9]{4}\-[0-9]{2}\-[0-9]{2})/', views.payments_detail,
        name='accounting_payments_detail'),
    url(r'^betalinger/', views.payments, name='accounting_payments'),
)