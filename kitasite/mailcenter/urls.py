from django.conf.urls.defaults import *

from mailcenter import views

urlpatterns = patterns('',
    url(r'^show/(?P<mail_id>[0-9]+)/send/', views.send_mails, name='mailcenter_send'),
    url(r'^show/(?P<mail_id>[0-9]+)/preview/', views.send_test_mail, name='mailcenter_send_test'),
    url(r'^list/', views.list_mails, name='mailcenter_list'),
    url(r'^show/(?P<mail_id>[0-9]+)/$', views.show_mail, name='mailcenter_view'),
    url(r'^show/(?P<mail_id>[0-9]+|new)/edit/', views.edit_mail, name='mailcenter_edit'),
)