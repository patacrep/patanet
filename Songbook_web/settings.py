# -*- coding: utf-8 -*-
"""
Django settings for Songbook-web project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(PROJECT_ROOT, ...)
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'l%a%^4avc2f&yr*gs&)_0@ls#2__l8fx&qyn#t2jjyo^#x2%bo'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TEMPLATE_CONTEXT': True,
}


ALLOWED_HOSTS = []

APPEND_SLASH = False

# Administrateurs
ADMINS = (('Luthaf', 'luthaf@yahoo.fr'))

DEFAULT_FROM_EMAIL = ''  # webmaster@nom.du.site

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)
INSTALLED_APPS += (
    'south',
    'background_task',
)
INSTALLED_APPS += (
    'generator',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'Songbook_web.urls'

WSGI_APPLICATION = 'Songbook_web.wsgi.application'


AUTHENTICATION_BACKENDS = (
    'generator.backends.EmailAuthBackend',
)

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'db.sqlite3'),
        'USER':'',
        'PASSWORD':'',
        'HOST':'',
        'PORT':'',
        'ATOMIC_REQUESTS': True,
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGE_CODE = 'fr-FR'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True

gettext = lambda x: x

LANGUAGES = (
('fr', gettext('French')),
('en', gettext('English')),)


STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = '/data/'
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, "generator/static/"),
    os.path.join(PROJECT_ROOT, "PDFs"),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Templates dans le dossier template
TEMPLATE_DIRS = (os.path.join(PROJECT_ROOT, 'templates/'),)

TEMPLATE_CONTEXT_PROCESSORS = (
        "django.contrib.auth.context_processors.auth",
        "django.core.context_processors.debug",
        "django.core.context_processors.i18n",
        "django.core.context_processors.media",
        "django.core.context_processors.static",
        "django.core.context_processors.request",
        "django.core.context_processors.tz",
        "django.contrib.messages.context_processors.messages",
        )

LOGIN_URL = '/user/login'
LOGIN_REDIRECT_URL = '/user/'

# Path to the root of the songbook repo, where the tools are to be found
SONG_PROCESSOR_DIR = os.path.join(PROJECT_ROOT, 'songbook-core/')
# Path to the songs directory (*.sg files) from the songbook repo
SONGS_LIBRARY_DIR = os.path.join(SONG_PROCESSOR_DIR, 'songs/')
# Path to the location where songbooks are stored
SONGBOOKS_DIR = os.path.join(PROJECT_ROOT, 'songbooks/')
# Path to the location where generated PDFs are stored
SONGBOOKS_PDFS = os.path.join(PROJECT_ROOT, 'PDFs')

SOUTH_TESTS_MIGRATE = False

try:
    from local_settings import *
except ImportError:
    pass
