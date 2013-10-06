
def site_urls(request):
    from django.conf import settings
    return {'SITE_URL': settings.SITE_URL,
            'DEBUG': settings.DEBUG,
            'VERSION': settings.VERSION,
            'request': request}
