# Django settings for expertsrc project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# change this to the absolute path to the dir where the checked-out expertsrc git repository lives
# make sure that this ends with a trailing slash
PROJECT_ROOT = '/home/apagan/'

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', 
        'NAME': 'expertsrc',                      
        'USER': 'apagan',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
    'goby': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', 
        'NAME': 'goby',
        'USER': 'apagan',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# Make this unique, and don't share it with anybody.
SECRET_KEY = '30b6dyuma$uec6ooicb75glkwe6awb@fqgof(k=ixp*f(5h139'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
#    'ui.middleware.SearchPath',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
)

ROOT_URLCONF = 'expertsrc.urls'

TEMPLATE_DIRS = (
    PROJECT_ROOT + "expertsrc/www/templates/",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'ui',
    'django.contrib.admin',
    'south',
)

AUTH_PROFILE_MODULE = 'ui.UserProfile'

STATIC_DOC_ROOT =  PROJECT_ROOT + "expertsrc/www/static"

TEST_DOMAIN_NAME = 'ski'

import logging

logging.basicConfig(
    filename = '/home/apagan/logs/err.log',
    level = logging.DEBUG,
    format = '%(asctime)s %(message)s',
)

LOGIN_URL = '/login'

STATIC_URL = '/media/'

TAMER_URL = 'http://modis.csail.mit.edu:8080'

TAMER_DB = 'goby'

WATCHER_LOGFILE = '/home/apagan/logs/watchers.log'
