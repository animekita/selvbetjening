from django.conf.urls.defaults import patterns, url

import views

urlpatterns = patterns('',
    url(r'^events/(?P<event_id>.+)/checkin/(?P<user_id>.+)/', views.event_usercheckin,
        name='eventmode_usercheckin'),
    url(r'^events/(?P<event_id>.+)/checkin/', views.event_checkin,
        name='eventmode_checkin'),
    url(r'^events/(?P<event_id>.+)/tilvalg/$', views.event_options,
        name='eventmode_options'),
    url(r'^events/(?P<event_id>.+)/statistik/$', views.event_statistics,
        name='eventmode_statistics'),
    url(r'^events/(?P<event_id>.+)/tilvalg/(?P<option_id>.+)', views.event_options_detail,
        name='eventmode_options_detail'),
    url(r'^login/$', views.login,
        name='eventmode_login'),
    url(r'^logud/$', views.logout,
        name='eventmode_logout'),
)