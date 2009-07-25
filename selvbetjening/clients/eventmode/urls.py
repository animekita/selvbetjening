from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
    url(r'^checkin/(?P<user_id>.+)/change/', views.change_selections,
        name='eventmode_change_selections'),
    url(r'^checkin/(?P<user_id>.+)/checkin/', views.checkin,
        name='eventmode_checkin'),
    url(r'^checkin/(?P<user_id>.+)/checkout/', views.checkout,
        name='eventmode_checkout'),
    url(r'^checkin/(?P<user_id>.+)/billing/', views.billing,
        name='eventmode_billing'),
    url(r'^login/$', views.login,
        name='eventmode_login'),
    url(r'^logud/$', views.logout,
        name='eventmode_logout'),
    url(r'^', views.list_attendees,
        name='eventmode_list_attendees'),
)