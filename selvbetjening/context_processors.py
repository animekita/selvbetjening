from selvbetjening.data.members import messaging
from selvbetjening.core.selvadmin.admin import site

def site_urls(request):
    from django.conf import settings
    return {'MEDIA_URL': settings.MEDIA_URL,
            'SITE_URL' : settings.SITE_URL,
            'DEBUG' : settings.DEBUG,
            'session_message' : messaging.read(request)}

def admin_navigation(request):
    return {'ADMIN_NAVIGATION': site.Menu.links.values()}
