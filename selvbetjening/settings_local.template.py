# debug
import sys

DEBUG = False
TEMPLATE_DEBUG = DEBUG
STATIC_DEBUG = DEBUG

# database
DATABASE_ENGINE = 'mysql' # mysql, sqlite3
DATABASE_NAME = 'kita_selv'
DATABASE_USER = 'root'
DATABASE_PASSWORD = ''

DATABASES = {
            'default': {
                'NAME': 'dbname',
                'ENGINE': 'django.db.backends.sqlite3' if 'test' in sys.argv else 'django.db.backends.mysql',
                'USER': 'dbuser',
                'PASSWORD': 'dbpassword',
                'OPTIONS': {} if 'test' in sys.argv else {'init_command': 'SET storage_engine=INNODB'},
                },
            }

# Site url (no trailing slash)
SITE_URL = 'http://'

# Absolute path to the directory that holds media - uploaded files
# USE TRAILING SLASH
MEDIA_ROOT = '/path/to/media/'

# URL that handles the media served from MEDIA_ROOT
# USE TRAILING SLASH
MEDIA_URL = 'http://media/'

# Absolute path to the directory that holds static files - javascript, css etc.
# USE TRAILING SLASH
STATIC_ROOT = '/path/to/static/files/'

# URL that handles the static files served from STATIC_ROOT
# USE TRAILING SLASH
STATIC_URL = 'http://static/'

# URL prefix for admin media
# USE TRAILING SLASH
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

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

"""
NOTIFY_VANILLAFORUM['example'] = {'database_id' : 'DATABASE_ID',
                                  'default_role_id' : 'default_ROLE_ID'}
"""
NOTIFY_VANILLAFORUM = []