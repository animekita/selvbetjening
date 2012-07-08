from selvbetjening.settings_base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
# ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'NAME': 'default',
        'ENGINE': 'django.db.backends.sqlite3',
        },
    'ext_database1': {
        'NAME': 'ext_database1',
        'ENGINE': 'django.db.backends.sqlite3',
        },
    'ext_database2': {
        'NAME': 'ext_database2',
        'ENGINE': 'django.db.backends.sqlite3',
        }
}

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'lic-@(-)mi^b&amp;**h1ggnbyya2qiivaop-@c#3@m3w%m1o73j8@'

ROOT_URLCONF = 'selvbetjening.urls'

# installed applications
INSTALLED_APPS.extend([
    'selvbetjening.viewbase.forms',
    'selvbetjening.viewbase.googleanalytics',
    'selvbetjening.viewbase.copyright',

    'selvbetjening.portal.quickregistration',
    'selvbetjening.portal.profile',
    'selvbetjening.portal.eventregistration',

    'selvbetjening.notify',
    'selvbetjening.notify.concrete5',
    'selvbetjening.notify.proftpd',
    'selvbetjening.notify.externaldjango',
    'selvbetjening.notify.vanillaforum',

    'selvbetjening.sadmin.base',
    'selvbetjening.sadmin.members',
    'selvbetjening.sadmin.events',
    'selvbetjening.sadmin.mailcenter',

    'selvbetjening.api.eventsapi',

    'selvbetjening.scheckin.legacy',

    ])

