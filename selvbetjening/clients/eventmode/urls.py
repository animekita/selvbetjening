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

    url(r'^user/create/', views.create_user,
        name='eventmode_create_user'),
    url(r'^user/add/', views.add_user,
        name='eventmode_add_user'),

    url(r'^notes/(?P<note_id>[0-9]+)/', views.notes,
        name='eventmode_note'),
    url(r'^notes/', views.notes,
        name='eventmode_notes'),
    url(r'^logs/', views.logs,
        name='eventmode_logs'),

    url(r'^login/$', views.login,
        name='eventmode_login'),
    url(r'^logud/$', views.logout,
        name='eventmode_logout'),
    url(r'^', views.list_attendees,
        name='eventmode_list_attendees'),
)