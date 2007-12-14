def site_urls(request):
    from django.conf import settings
    return {'MEDIA_URL': settings.MEDIA_URL, 'SITE_URL' : settings.SITE_URL}
