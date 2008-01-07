def site_urls(request):
    from django.conf import settings
    return {'MEDIA_URL': settings.MEDIA_URL, 'SITE_URL' : settings.SITE_URL, 
            'GOOGLE_ANALYTICS_ACCOUNT' : settings.GOOGLE_ANALYTICS_ACCOUNT,
        'DEBUG' : settings.DEBUG}
