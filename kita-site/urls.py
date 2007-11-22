from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from django.contrib.auth import views as auth_views

urlpatterns = patterns('',
    url(r'^$',
        redirect_to,
        {'url' : '/login/'},
        name = 'home'),
    
    url(r'^login/$',
        auth_views.login,
        {'template_name': 'registration/login.html'},
        name='auth_login'),
    
    url(r'^logud/$',
        auth_views.logout,
        {'template_name': 'registration/logout.html'},
        name='auth_logout'),  
    
    url(r'^nulstil-kodeord/$',
        auth_views.password_reset,
        {'template_name':'registration/resetPassword.html'},
        name='auth_password_reset'),
    
    url(r'^nulstil-kodeord/done/$',
        auth_views.password_reset_done,
        {'template_name':'registration/resetPasswordDone.html'},
        name='auth_password_reset_done'),    
    
    (r'^profil/', include('kita-site.members.urls')),
    (r'^bliv-medlem/', include('kita-site.registration.urls')),    
    (r'^events/', include('kita-site.events.urls')),
    (r'^migrate/', include('kita-site.migration.urls')),

    # Admin urls
    (r'^admin/', include('django.contrib.admin.urls')),
)
