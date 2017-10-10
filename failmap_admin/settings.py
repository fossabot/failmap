"""Django settings for failmap-admin project.

Generated by 'django-admin startproject' using Django 1.9.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

from colorlog import ColoredFormatter

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Changed BASE_DIR so templates need to include the module and such. The idea
# was that otherwise the wrong template could be used when they have the same name
# over different dirs. Is this correct?
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'ditisgeengeheimvriendachtjedatditeenwachtwoordwas')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', False)

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

INTERNAL_IPS = [
    '127.0.0.1'
]

# Application definition

INSTALLED_APPS = [
    'jet.dashboard',
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'failmap_admin.fail',
    'failmap_admin.organizations',
    'failmap_admin.scanners',
    'failmap_admin.map',
    'django_countries',
    'django.contrib.admindocs',
    'django.contrib.humanize',
    # Dal removed, since we use the admin site for custom commands.
    # 'dal',  # django-autocomplete-light, explicitly after admin, to not interfere with admin
    # 'dal_select2',  # django-autocomplete-light
    # 'cachalot',  # query cache, is not faster.
    # 'silk'  # works great for debugging.
    # debug_toolbar',  # debugging and optimization, seems mostly useless in json apps, don't use
]

try:
    import django_uwsgi
    INSTALLED_APPS += ['django_uwsgi', ]
except ImportError:
    # only configure uwsgi app if installed (ie: production environment)
    pass

MIDDLEWARE_CLASSES = [
    # 'silk.middleware.SilkyMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',  # admindocs

    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'failmap_admin.urls'

# template needed for admin template
# this step is missing in the django jet tutorial, maybe because it's fairly common.

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR + '/',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'failmap_admin.wsgi.application'

# Assume traffic is proxied from frontend loadbalancers
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

# Since we don't use anything specific from a db engine, we move to sqllite.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.' + os.environ.get('DB_ENGINE', 'sqlite3'),
        'NAME': os.environ.get('DB_NAME', 'db.sqlite3'),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
    },
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

# Go to admin: language_code = language_code.replace('_', '-').lower()
# AttributeError: 'NoneType' object has no attribute 'replace'
# while settings are loaded and Django uses LANGUAGE_CODE as default. What overrides this?
# a possible undesired solution, http://source.mihelac.org/2009/11/12/django-set-language-for-admin/

# http://stackoverflow.com/questions/1832709/django-how-to-make-translation-work
# shoddy documentation on dashes and underscores... different than the "ll" suggestion.
# LANGUAGE_CODE = 'en-gb'
LANGUAGES = (
    ('en', 'English'),
    ('nl', 'Dutch'),
)

LANGUAGE_CODE = 'nl'

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True

# Disable timezones when using sqlite as it causes (really) a lot of warnings about timezones during fixture import.
if 'sqlite' in DATABASES['default']['ENGINE']:
    USE_TZ = False
else:
    USE_TZ = True

# https://docs.djangoproject.com/en/1.11/topics/i18n/translation/#how-django-discovers-translations
# In all cases the name of the directory containing the translation is expected to be named using
# locale name notation. E.g. de, pt_BR, es_AR, etc.
LOCALE_PATHS = ['locale']


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

# Absolute path to aggregate to and serve static file from.
STATIC_ROOT = '/srv/failmap-admin/static/'

TEST_RUNNER = 'failmap_admin.testrunner.PytestTestRunner'

# From the Jet documentation, a different color for a different season.
JET_THEMES = [
    {
        'theme': 'default',  # theme folder name
        'color': '#47bac1',  # color of the theme's button in user menu
        'title': 'Default'  # theme title
    },
    {
        'theme': 'green',
        'color': '#44b78b',
        'title': 'Green'
    },
    {
        'theme': 'light-green',
        'color': '#2faa60',
        'title': 'Light Green'
    },
    {
        'theme': 'light-violet',
        'color': '#a464c4',
        'title': 'Light Violet'
    },
    {
        'theme': 'light-blue',
        'color': '#5EADDE',
        'title': 'Light Blue'
    },
    {
        'theme': 'light-gray',
        'color': '#222',
        'title': 'Light Gray'
    }
]

# see: https://github.com/geex-arts/django-jet/blob/
#   fea07040229d1b56800a7b8e6234e5f9419e2114/docs/config_file.rst
# required for custom modules
JET_APP_INDEX_DASHBOARD = 'failmap_admin.organizations.dashboard.CustomIndexDashboard'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',  # sys.stdout
            'formatter': 'color',
        },
    },
    'formatters': {
        'debug': {
            'format': '%(asctime)s\t%(levelname)-8s - %(filename)-20s:%(lineno)-4s - '
                      '%(funcName)20s() - %(message)s',
        },
        'color': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(asctime)s\t%(levelname)-8s - '
                      '%(filename)s:%(lineno)-4s - %(funcName)40s() - %(message)s',
            'datefmt': '%Y%-m-%d %H:%M',
            'log_colors': {
                'DEBUG':    'green',
                'INFO':     'white',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'bold_red',
            },
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],    # used when there is no logger defined or loaded.
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'failmap_admin.scanners': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'propagate': False,  # if you don't the root logger will also output.
            # see: https://stackoverflow.com/questions/19561058/duplicate-output-in-simple-p...
        },
        'failmap_admin.map': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'propagate': False,  # if you don't the root logger will also output.
            # see: https://stackoverflow.com/questions/19561058/duplicate-output-in-simple-p...
        },
    },
}

# add a slash at the end so we know it's a directory.
# Don't want to do things to anything in /
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__)) + '/'
VENDOR_DIR = os.path.abspath(os.path.dirname(__file__) + '/../vendor/') + '/'
# print(PROJECT_DIR)
# print(VENDOR_DIR)
# todo: chrome works only for mac. Not yet for linux.
TOOLS = {
    'chrome': {
        'executable': {
            'Darwin': VENDOR_DIR + "Google Chrome.app/Contents/MacOS/Google Chrome",
            'Linux': "/dev/null",
        },
        'screenshot_output_dir': PROJECT_DIR + 'map/static/images/screenshots/',
    },
    'firefox': {
        'executable': {
            'Darwin': VENDOR_DIR + "Firefox.app/Contents/MacOS/firefox",
            'Linux': "/dev/null",
        },
        'screenshot_output_dir': PROJECT_DIR + 'map/static/images/screenshots/',
    },
    'theHarvester': {
        'executable': VENDOR_DIR + "theHarvester/theHarvester.py",
        'output_dir': PROJECT_DIR + "scanners/resources/output/theHarvester/"
    },
    'dnsrecon': {
        'executable': VENDOR_DIR + "dnsrecon/dnsrecon.py",
        'output_dir': PROJECT_DIR + "scanners/resources/output/dnsrecon/",
        'wordlist_dir': PROJECT_DIR + "scanners/resources/wordlists/",
    },
    'sslscan': {
        'executable': {
            'Darwin': 'sslscan',
            'Linux': 'sslscan',
        },
        'report_output_dir': PROJECT_DIR + "scanners/resources/output/sslscan/",
    },
    'openssl': {
        'executable': {
            'Darwin': 'openssl',
            'Linux': 'openssl',
        },
    },
    'TLS': {
        'cve_2016_2107': VENDOR_DIR + 'CVE-2016-2107-padding-oracle/main.go',
        'cve_2016_9244': VENDOR_DIR + 'CVE-2016-9244-ticketbleed/ticketbleed.go',
        'cert_chain_resolver': {
            'Darwin': VENDOR_DIR + 'cert-chain-resolver/cert-chain-resolver-darwin',
            'Linux': VENDOR_DIR + 'cert-chain-resolver/cert-chain-resolver-linux',
        }
    }
}
# exit(-1)


# Celery 4.0 settings
# Pickle can work, but you need to use certificates to communicate (to verify the right origin)
# It's preferable not to use pickle, yet it's overly convenient as the normal serializer can not
# even serialize dicts.
# http://docs.celeryproject.org/en/latest/userguide/configuration.html
CELERY_accept_content = ['pickle', 'yaml']
CELERY_task_serializer = 'pickle'
CELERY_result_serializer = 'pickle'
