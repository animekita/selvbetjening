def site_urls(request):
    from django.conf import settings
    return {'media_url': settings.MEDIA_URL, 'site_url' : settings.SITE_URL}
