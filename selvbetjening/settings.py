# Django settings
import os

DIRNAME = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'sqlite.db'

DEFAULT_FROM_EMAIL = 'noreply@anime-kita.dk'
SERVER_EMAIL = 'noreply@anime-kita.dk'

AUTH_PROFILE_MODULE = 'members.UserProfile'
LOGIN_REDIRECT_URL = '/profil/'
LOGIN_URL = '/profil/login/'

LOG_FILE = 'log.log'

TIME_ZONE = 'Denmark/Copenhagen'
LANGUAGE_CODE = 'da-dk'

SITE_ID = 1

USE_I18N = True

SITE_URL = 'http://localhost:8000'
MEDIA_ROOT = os.path.join(DIRNAME, 'static/')
MEDIA_URL = 'http://localhost:8000/static/'
ADMIN_MEDIA_PREFIX = '/media/'

SECRET_KEY = 'change:me'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'selvbetjening.clients.eventmode.middleware.EventmodeMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'selvbetjening.context_processors.site_urls',
    'selvbetjening.clients.eventmode.context_processors.eventmode',
    'django.core.context_processors.i18n',
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    )

ROOT_URLCONF = 'selvbetjening.urls'

TEMPLATE_DIRS = (
    os.path.join(DIRNAME, 'templates')
)

INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.markup',

    'selvbetjening.data.events',
    'selvbetjening.data.members',
    'selvbetjening.data.invoice',

    'selvbetjening.viewhelpers.forms',
    'selvbetjening.viewhelpers.googleanalytics',
    'selvbetjening.viewhelpers.copyright',

    'selvbetjening.clients.profile',
    'selvbetjening.clients.eventmode',
    'selvbetjening.clients.mailcenter',
    'selvbetjening.clients.quickregistration',
    'selvbetjening.clients.eventregistration',

    'selvbetjening.api.sso',
)

# Initialize Logging
import logging

logging.basicConfig(
    level=logging.NOTSET,
    format='%(asctime)s %(clientip)s %(user)s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M',
    filename=LOG_FILE,
    filemode='a'
)
logging.getLogger('').setLevel(logging.NOTSET)

# Eventmode checkin modules
EVENTMODE_CHECKIN_PROCESSORS = (
    'selvbetjening.data.membership.checkin_processors.membership',
    'selvbetjening.data.events.checkin_processors.options',
)
