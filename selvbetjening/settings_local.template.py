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

# Notify configurations

"""
NOTIFY_CONCRETE5['example'] = {'database_id' : 'DATABASE_ID'}
"""
NOTIFY_CONCRETE5 = []

"""
NOTIFY_PROFTPD['example'] = {'database_id' : 'DATABASE_ID',
                             'default_gid' : 1,
                             'default_uid' : 1,
                             'ftp_dir' : '/var/ftp/',
                             'username_format' : '%s@domain.tld'}
"""
NOTIFY_PROFTPD = []