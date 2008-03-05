from django.conf.urls.defaults import *

from eventmode import views

urlpatterns = patterns('',
    url(r'^(?P<event_id>.+)/checkin/(?P<user_id>.+)/', views.event_usercheckin, 
        name='eventmode_usercheckin'),
    url(r'^(?P<event_id>.+)/checkin/', views.event_checkin, 
        name='eventmode_checkin'),
    url(r'^(?P<event_id>.+)/tilvalg/$', views.event_options, 
        name='eventmode_options'),
    url(r'^(?P<event_id>.+)/tilvalg/(?P<option_id>.+)', views.event_options_detail,
        name='eventmode_options_detail'),        
    url(r'^$', views.event_list, 
        name='eventmode_list'),
    url(r'^aktiver/$', views.activate_mode, 
        name='eventmode_activate'),
    url(r'^deaktiver/$', views.deactivate_mode, 
        name='eventmode_deactivate'), 
    url(r'^info/$', views.info, 
        name='eventmode_info'), 
)