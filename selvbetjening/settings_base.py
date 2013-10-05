# Base settings for all Selvbetjening installations, overrride this with a
# per. instance settings.py file.

# pre setup
import selvbetjening
import os
import sys

SELV_DIRNAME = os.path.abspath(os.path.dirname(__file__))

from selvbetjening import contrib
contrib.add_contrib_to_python_path()

VERSION = selvbetjening.__version__

# Debugging
DEBUG = False
TEMPLATE_DEBUG = DEBUG
STATIC_DEBUG = DEBUG
INTERNAL_IPS = ('127.0.0.1',)

# Application settings
AUTH_PROFILE_MODULE = 'members.UserProfile'
LOGIN_REDIRECT_URL = '/profil/'
LOGIN_URL = '/profil/login/'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Copenhagen'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'da-dk'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    )

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
    )

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware'
]

TEMPLATE_CONTEXT_PROCESSORS = (
    'selvbetjening.context_processors.site_urls',
    'selvbetjening.sadmin2.context_processors.sadmin2_navigation',

    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.csrf',
    'django.core.context_processors.request',

    "django.contrib.auth.context_processors.auth",
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
    'crispy_forms',
    'sorl.thumbnail',
    'crumbs',
    'debug_toolbar',
    'django_extensions',
    'navtree',
    'django_assets',

    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'selvbetjening.core.events',
    'selvbetjening.core.members',
    'selvbetjening.core.mailcenter',

    'selvbetjening.sadmin2',

    'selvbetjening.viewbase.branding'
]

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
            },
        }
}

SKIP_SOUTH_TESTS = True
SOUTH_TESTS_MIGRATE = False

TEST_RUNNER = 'selvbetjening.core.testrunner.IncludingTestSuiteRunner'
TEST_INCLUDE = ['selvbetjening']

CRISPY_TEMPLATE_PACK = 'bootstrap3'

DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False
}

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
#    'debug_toolbar.panels.profiling.ProfilingDebugPanel'
)

POLICY = dict()
POLICY['PORTAL.EVENTREGISTRATION.SKIP_CONFIRMATION_ON_EMPTY_OPTIONS'] = False
