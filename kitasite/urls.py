from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to, direct_to_template
from django.contrib.auth import views as auth_views

from core.views import frontpage

urlpatterns = patterns('',
    url(r'^$',
        frontpage,
        name = 'home'),
    
    url(r'^login/$',
        auth_views.login,
        {'template_name': 'registration/login.html'},
        name='auth_login'),
    
    url(r'^logud/$',
        auth_views.logout,
        {'template_name': 'registration/logout.html', 'next_page' : '/login/'},
        name='auth_logout'),  
    
    url(r'^nulstil-kodeord/$',
        auth_views.password_reset,
        {'template_name':'registration/resetPassword.html'},
        name='auth_password_reset'),
    
    url(r'^nulstil-kodeord/done/$',
        auth_views.password_reset_done,
        {'template_name':'registration/resetPasswordDone.html'},
        name='auth_password_reset_done'),    

    url(r'^behandling-af-personoplysninger/$',
        direct_to_template,
        {'template' : 'data-rules.html'},
        name='data_rules'),
    
    (r'^profil/', include('kita-site.members.urls')),
    (r'^bliv-medlem/', include('kita-site.registration.urls')),    
    (r'^events/', include('kita-site.events.urls')),
    (r'^migrate/', include('kita-site.migration.urls')),
    (r'^accounting/', include('kita-site.accounting.urls')),
    (r'^booking/', include('kita-site.booking.urls')),
    (r'^eventmode/', include('kita-site.eventmode.urls')),
    (r'^mailcenter/', include('kita-site.mailcenter.urls')),
    
    # Main site redirection urls
    url(r'^goto/ordensregler/$',
        redirect_to,
        {'url' : 'http://www.anime-kita.dk/regler.html'},
        name = 'goto_eventrules'),
    
    url(r'goto/vedtaegter/$',
        redirect_to,
        {'url' : 'http://www.anime-kita.dk/vedtaegter.html'},
        name = 'goto_regulations'),

    # Admin urls
    (r'^admin/', include('django.contrib.admin.urls')),
)
