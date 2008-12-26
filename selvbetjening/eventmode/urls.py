from django.conf.urls.defaults import patterns, url

import views

urlpatterns = patterns('',
    url(r'^checkin/(?P<user_id>.+)/', views.event_usercheckin,
        name='eventmode_usercheckin'),
    url(r'^checkin/', views.event_checkin,
        name='eventmode_checkin'),
    url(r'^tilvalg/$', views.event_options,
        name='eventmode_options'),
    url(r'^tilvalg/(?P<option_id>.+)', views.event_options_detail,
        name='eventmode_options_detail'),
    url(r'^login/$', views.login,
        name='eventmode_login'),
    url(r'^logud/$', views.logout,
        name='eventmode_logout'),
    url(r'^', views.index,
        name='eventmode_index'),
)