from selvbetjening.core.members import messaging
from selvbetjening.sadmin.base import sadmin

def site_urls(request):
    from django.conf import settings
    return {'MEDIA_URL': settings.MEDIA_URL,
            'SITE_URL': settings.SITE_URL,
            'DEBUG': settings.DEBUG,
            'VERSION': settings.VERSION,
            'session_message': messaging.read(request),
            'sadmin_main_menu': sadmin.main_menu,
            'request': request}
