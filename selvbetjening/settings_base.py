# Base settings for all Selvbetjening installations, overrride this with a
# per. instance settings.py file.

# pre setup
import os
SELV_DIRNAME = os.path.abspath(os.path.dirname(__file__))

from selvbetjening import contrib
contrib.add_contrib_to_python_path()

# debugging
DEBUG = False
TEMPLATE_DEBUG = DEBUG
STATIC_DEBUG = DEBUG

# base settings
AUTH_PROFILE_MODULE = 'members.UserProfile'

SITE_ID = 1

USE_I18N = True

TIME_ZONE = 'Denmark/Copenhagen'
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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'selvbetjening.context_processors.site_urls',
    'django.core.context_processors.i18n',
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
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

    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',

    'selvbetjening.core.selvadmin',

    'selvbetjening.data.events',
    'selvbetjening.data.members',
    'selvbetjening.data.invoice',
    'selvbetjening.data.translation',
]

# tinymce config
TINYMCE_DEFAULT_CONFIG = {
    'language': 'en',
    'theme' : 'advanced',
    'width' : '600',
    'height' : '300',
    'theme_advanced_toolbar_location' : "top",
    'theme_advanced_toolbar_align' : "left",
    'theme_advanced_buttons1' : "fullscreen,separator,preview,separator,bold,italic,underline,strikethrough,separator,bullist,numlist,outdent,indent,separator,undo,redo,separator,link,unlink,separator,cleanup,help,separator,code",
    'theme_advanced_buttons2' : "",
    'theme_advanced_buttons3' : "",
    'plugins' : "preview,fullscreen",
}
