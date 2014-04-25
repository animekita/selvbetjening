
from django.conf import settings


def site_urls(request):

    return {
        'request': request,
        'DEBUG': settings.DEBUG,
        'VERSION': settings.VERSION,
        'STATIC_URL': settings.STATIC_URL,
        'MEDIA_URL': settings.MEDIA_URL,
        'POLICY': settings.POLICY
    }
