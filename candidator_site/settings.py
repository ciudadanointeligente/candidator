# encoding=UTF-8
"""
Django settings for candidator project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'b_d@h*^q(#944l$7tk$r#kjl48e!idet%x-9@fdd6ogb7a_-io'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'grappelli',
    'sorl.thumbnail',
    'tastypie',
    'registration',
    'elections',
    'candidator',
    'report_objects',
    'django_extensions',
    # Django-registration
    
    # Tastypie, RESTful APIs for Django:
    'smart_profile',
    'markdown_deux',
    'django_nose',

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'candidator_site.urls'

WSGI_APPLICATION = 'candidator_site.wsgi.application'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

SITE_ID = 1
USER_FILES = 'static-files'
# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

DEFAULT_PERSONAL_DATA = ['Edad', 'Estado civil', u'Profesión', u'Género']
DEFAULT_BACKGROUND_CATEGORIES = {u'Educación': [u'Educación primaria', u'Educación secundaria', u'Educación superior'],
                                 u'Antecedentes laborales': [u'Último trabajo']}

DEFAULT_QUESTIONS = [{
    'Category':u'Educación',
    'Questions':[
        {
            'question':u'¿Crees que Chile debe tener una educación gratuita?',
            'answers':[u'Sí',u'No']
        },
        {
            'question':u'¿Estas de acuerdo con la desmunicipalización?',
            'answers':[u'Sí',u'No']
        }
    ]
}]


USERVOICE_CLIENT_KEY = 'THIS IS JUST AN EXAMPLE YOU SHOLD CHANGE THIS'
GOOGLE_ANALYTICS_ACCOUNT_ID = "GOOGLE ANALYTICS ACCOUNT ID"


#EMBEDED WEBPAGE FOR TESTING

EMBEDED_TEST_WEB = 'http://localhost:8000/admin/cei-2012/embeded'

try:
    from local_settings import *
except ImportError:
    pass

