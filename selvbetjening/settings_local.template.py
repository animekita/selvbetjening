# debug
DEBUG = False
TEMPLATE_DEBUG = DEBUG
STATIC_DEBUG = DEBUG

# database
DATABASE_ENGINE = 'mysql' # mysql, sqlite3
DATABASE_NAME = 'kita_selv'
DATABASE_USER = 'root'
DATABASE_PASSWORD = ''

# Site url (no trailing slash)
SITE_URL = 'http://'

# Absolute path to the directory that holds media (with trailing slash).
MEDIA_ROOT = '/static/'

# URL that handles the media served from MEDIA_ROOT (with trailing slash)
MEDIA_URL = 'http://static/'

# URL prefix for admin media (with trailing slash).
ADMIN_MEDIA_PREFIX = '/media/'

# session settings
SESSION_COOKIE_NAME = 'kita_auth_token'
SESSION_COOKIE_DOMAIN = '.alpha.kita.dk'

# Change this key!
SECRET_KEY = 'change:me'