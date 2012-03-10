from selvbetjening.settings_base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
STATIC_DEBUG = DEBUG

import os
DIRNAME = os.path.abspath(os.path.dirname(__file__))

# email
DEFAULT_FROM_EMAIL = 'noreply@anime-kita.dk'
SERVER_EMAIL = 'noreply@anime-kita.dk'

# various settings
ROOT_URLCONF = 'selvbetjening.urls'

ADMINS = (
    #('admin', 'admin@example.org'),
)

# template directories
TEMPLATE_DIRS = [
    os.path.join(DIRNAME, 'templates')
] + TEMPLATE_DIRS

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

# this would normally be placed in the local settings file
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

SITE_URL = 'dev.anime-kita.dk'

STATIC_URL = 'http://localhost:8000/static/'
STATIC_ROOT = os.path.join(DIRNAME, '..', '..', '..', 'static', 'trunk')
