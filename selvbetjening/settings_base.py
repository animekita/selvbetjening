# Base settings for all Selvbetjening installations, overrride this with a
# per. instance settings.py file.

# pre setup
import selvbetjening
import os
SELV_DIRNAME = os.path.abspath(os.path.dirname(__file__))

from selvbetjening import contrib
contrib.add_contrib_to_python_path()

VERSION = selvbetjening.__version__

# debugging
DEBUG = False
TEMPLATE_DEBUG = DEBUG
STATIC_DEBUG = DEBUG
INTERNAL_IPS = ('127.0.0.1',)

# base settings
AUTH_PROFILE_MODULE = 'members.UserProfile'

SITE_ID = 1

USE_I18N = True

TIME_ZONE = 'Europe/Copenhagen'
LANGUAGE_CODE = 'da-dk'

LOGIN_REDIRECT_URL = '/profil/'
LOGIN_URL = '/profil/login/'

# base template loaders, middleware and context processors
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
#    'debug_toolbar.middleware.DebugToolbarMiddleware'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'selvbetjening.context_processors.site_urls',

    'django.core.context_processors.media',
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.csrf',
    'django.core.context_processors.request',

    'django.contrib.messages.context_processors.messages',
)

# base template directories
TEMPLATE_DIRS = [
    os.path.join(SELV_DIRNAME, 'templates')
]

# base installed applications (dependencies)
INSTALLED_APPS = [
    'countries',
    'south',
    'mailer',
    'uni_form',
    'sorl.thumbnail',
    'crumbs',
    'debug_toolbar',
    'django_extensions',
    'navtree',

    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.messages',

    'selvbetjening.core.database',

    'selvbetjening.core.events',
    'selvbetjening.core.members',
    'selvbetjening.core.invoice',
    'selvbetjening.core.translation',
    'selvbetjening.core.logger',
    'selvbetjening.core.mailcenter',
]

DATABASE_ROUTERS = ['selvbetjening.core.database.dbrouter.DatabaseRouter',]

SOUTH_TESTS_MIGRATE = False