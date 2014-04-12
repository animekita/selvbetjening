# Base settings for all Selvbetjening installations, overrride this with a
# per. instance settings.py file.

import selvbetjening
import os

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
AUTH_USER_MODEL = 'user.SUser'

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
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'selvbetjening.core.logging.middleware.SelvbetjeningGlobalRequestMiddleware',
    'selvbetjening.sadmin2.middleware.RequireLoginMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware'
]

TEMPLATE_CONTEXT_PROCESSORS = (
    'selvbetjening.context_processors.site_urls',
    'selvbetjening.sadmin2.context_processors.sadmin2_navigation',
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
    'mailqueue',
    'crispy_forms',
    'sorl.thumbnail',
    'debug_toolbar',
    'django_extensions',
    'pipeline',

    'provider',
    'provider.oauth2',
    'tastypie',

    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'selvbetjening.core.user',
    'selvbetjening.core.members',
    'selvbetjening.core.events',
    'selvbetjening.core.mailcenter',
    'selvbetjening.core.logging',

    'selvbetjening.businesslogic.members',
    'selvbetjening.businesslogic.events',

    'selvbetjening.sadmin2'
]

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
        },
        'selvbetjening_db_log': {
            'level': 'INFO',
            'class': 'selvbetjening.core.logging.log.DBHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True
        },
        'selvbetjening': {
            'handlers': ['selvbetjening_db_log'],
            'level': 'INFO',
            'propagate': True
        }
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

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]

# Static file management (using django-pipeline)

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.jsmin.JSMinCompressor'
PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.cssmin.CSSMinCompressor'

PIPELINE_CSS = {
    'combined': {
        'source_filenames': [
            'css/vendor/bootstrap.min.css',
            'css/vendor/font-awesome.min.css',
            'css/eventsingle.css'
        ],
        'output_filename': 'css/combined.css'
    },

    'sadmin2': {
        'source_filenames': (
            'sadmin2/css/bootstrap.3.0.0.min.css',
            'sadmin2/css/font-awesome.4.0.0.min.com',
            'sadmin2/css/nv.d3.css',
            'sadmin2/css/main.css'
        ),
        'output_filename': 'sadmin2/css/combined.css'
    }
}

PIPELINE_JS = {
    'combined': {
        'source_filenames': [
            'js/vendor/modernizr-2.6.2-respond-1.1.0.min.js',
            'js/vendor/jquery-2.0.3.min.js',
            'js/vendor/jquery.scrollTo-min.js',
            'js/vendor/bootstrap.min.js',
            'js/selvbetjening.core.events.js'
        ],
        'output_filename': 'js/combined.js',
    },

    'sadmin2': {
        'source_filenames': (
            'sadmin2/js/vendor/modernizr-2.6.2-respond-1.1.0.min.js',
            'sadmin2/js/vendor/jquery-2.0.3.min.js',
            'sadmin2/js/vendor/bootstrap.min.js',
            'sadmin2/js/vendor/jquery.autocomplete.min.js',
            'sadmin2/js/vendor/jquery.autosize.min.js',
            'sadmin2/js/vendor/jquery-ui-1.10.3.min.js',
            'sadmin2/js/vendor/d3.v3.js',
            'sadmin2/js/vendor/nv.d3.js',
            'sadmin2/js/main.js'
        ),
        'output_filename': 'sadmin2/js/combined.js',
    }
}

# Selvbetjening specific settings

POLICY = dict()
POLICY['PORTAL.EVENTREGISTRATION.SKIP_CONFIRMATION_ON_EMPTY_OPTIONS'] = False

# SAdmin2

SADMIN2_BASE_URL = 'sadmin2'  # don't add a trailing slash

# E-mail

MAILQUEUE_LIMIT = 50
MAILQUEUE_QUEUE_UP = True

# OAUTH settings

OAUTH_ENABLE_APPROVAL_PROMPT_BYPASS = True
