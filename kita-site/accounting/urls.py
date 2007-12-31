from django.conf.urls.defaults import *

from accounting import views

urlpatterns = patterns('',
    url(r'^bruger/(?P<user>.+)/historie/', views.payment_history, name='accounting_history'),
    url(r'^bruger/(?P<user>.+)/betal/', views.pay, name='accounting_pay'),
    url(r'^list/', views.list, name='accounting_list'),
)