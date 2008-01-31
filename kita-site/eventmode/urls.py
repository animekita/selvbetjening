from django.conf.urls.defaults import *

from eventmode import views

urlpatterns = patterns('',
    url(r'^(?P<event_id>.+)/checkin/(?P<user_id>.+)/', views.event_usercheckin, 
        name='eventmode_usercheckin'),
    url(r'^(?P<event_id>.+)/checkin/', views.event_checkin, 
        name='eventmode_checkin'),
    url(r'^$', views.event_list, 
        name='eventmode_list'),
)