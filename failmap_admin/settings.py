"""Django settings for failmap-admin project.

Generated by 'django-admin startproject' using Django 1.9.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""
import os

from pkg_resources import get_distribution

__version__ = get_distribution(__name__.split('.', 1)[0]).version

# this application can run in 2 modes: admin and frontend
# admin exposes all routes and uses no caching. It should be restricted in access
# frontend only exposes the visitor facing routes and serves with cache headers
APPNAME = os.environ.get('SERVICE_NAME', 'failmap-admin')

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

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,::1').split(',')

# allow better debugging for these clients
# https://docs.djangoproject.com/en/1.11/ref/settings/#internal-ips
INTERNAL_IPS = ['localhost', '127.0.0.1', '::1']

# Application definition

INSTALLED_APPS = [
    # needs to be before jet and admin to extend admin/base.html template
    'failmap_admin.app',
    # Jet admin dashboard
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
    'compressor',
    'django_celery_beat',
    'proxy',
    'django_statsd',
    # Dal removed, since we use the admin site for custom commands.
    # 'dal',  # django-autocomplete-light, explicitly after admin, to not interfere with admin
    # 'dal_select2',  # django-autocomplete-light
    # 'cachalot',  # query cache, is not faster.
    # 'silk'  # works great for debugging.
]

try:
    # hack to disable django_uwsgi app as it currently conflicts with compressor
    # https://github.com/django-compressor/django-compressor/issues/881
    if not os.environ.get('COMPRESS', False):
        import django_uwsgi  # NOQA

        INSTALLED_APPS += ['django_uwsgi', ]
except ImportError:
    # only configure uwsgi app if installed (ie: production environment)
    pass

# don't run this in production
try:
    import django_extensions  # NOQA

    INSTALLED_APPS += ['django_extensions']
except ImportError:
    pass

MIDDLEWARE_CLASSES = [
    # statsd metrics collection
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'django_statsd.middleware.GraphiteMiddleware',
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
DATABASE_OPTIONS = {
    'mysql': {'init_command': "SET sql_mode='STRICT_ALL_TABLES';"},

}
DATABASES_SETTINGS = {
    # persisten local database used during development (runserver)
    'dev': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get('DB_NAME', 'db.sqlite3'),
    },
    # sqlite memory database for running tests without
    'test': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get('DB_NAME', 'db.sqlite3'),
    },
    # for production get database settings from environment (eg: docker)
    'production': {
        'ENGINE': 'django.db.backends.' + os.environ.get('DB_ENGINE', 'mysql'),
        'NAME': os.environ.get('DB_NAME', 'failmap'),
        'USER': os.environ.get('DB_USER', 'failmap'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'failmap'),
        'HOST': os.environ.get('DB_HOST', 'mysql'),
        'OPTIONS': DATABASE_OPTIONS.get(os.environ.get('DB_ENGINE', 'mysql'), {})
    }
}
# allow database to be selected through environment variables
DATABASE = os.environ.get('DJANGO_DATABASE', 'dev')
DATABASES = {'default': DATABASES_SETTINGS[DATABASE]}

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

# Loaddata will show a massive amount of warnings, therefore use load-dataset. load-dataset will
# do exactly the same as loaddata, but will overwrite below flag preventing warnings.
USE_TZ = True

# https://docs.djangoproject.com/en/1.11/topics/i18n/translation/#how-django-discovers-translations
# In all cases the name of the directory containing the translation is expected to be named using
# locale name notation. E.g. de, pt_BR, es_AR, etc.
LOCALE_PATHS = ['locale']

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

# Absolute path to aggregate to and serve static file from.
if DEBUG:
    STATIC_ROOT = 'static'
else:
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
                      '%(message)s',
            'datefmt': '%Y%-m-%d %H:%M',
            'log_colors': {
                'DEBUG': 'green',
                'INFO': 'white',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            },
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],  # used when there is no logger defined or loaded.
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

# Add a slash at the end so we know it's a directory. Tries to somewhat prevents doing things in root.
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', os.path.abspath(os.path.dirname(__file__)) + '/')
VENDOR_DIR = os.environ.get('VENDOR_DIR', os.path.abspath(os.path.dirname(__file__) + '/../vendor/') + '/')

# A number of tools and outputs are grouped to easier have access to all of them.
# Our vendor directory contains a number of small tools that are hard to install otherwise.

TOOLS = {
    # Chrome and firefox are special cases: they install very easily and therefore don't need further grouping.
    'chrome': {
        'executable': {
            # os.platform is used to see what binaries should be used on a worker.
            'Darwin': os.environ.get(
                'CHROME_EXECUTABLE_DARWIN', "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            'Linux': os.environ.get(
                'CHROME_EXECUTABLE_LINUX', ""),
        },
        'screenshot_output_dir': OUTPUT_DIR + os.environ.get(
            'CHROME_SCREENSHOT_OUTPUT_DIR', 'map/static/images/screenshots/'),
    },
    # Chrome and firefox are special cases: they install very easily and therefore don't need further grouping.
    'firefox': {
        'executable': {
            # os.platform is used to see what binaries should be used on a worker.
            'Darwin': os.environ.get(
                'FIREFOX_EXECUTABLE_DARWIN', "/Applications/Firefox.app/Contents/MacOS/firefox"),
            'Linux': os.environ.get(
                'FIREFOX_EXECUTABLE_LINUX', ""),
        },
        'screenshot_output_dir': OUTPUT_DIR + os.environ.get(
            'FIREFOX_SCREENSHOT_OUTPUT_DIR', 'map/static/images/screenshots/'),
    },
    'theHarvester': {
        'executable': VENDOR_DIR + os.environ.get('THEHARVESTER_EXECUTABLE', "theHarvester/theHarvester.py"),
        'output_dir': OUTPUT_DIR + os.environ.get('THEHARVESTER_OUTPUT_DIR', "scanners/resources/output/theHarvester/"),
    },
    'dnsrecon': {
        'executable': VENDOR_DIR + os.environ.get('DNSRECON_EXECUTABLE', "dnsrecon/dnsrecon.py"),
        'output_dir': OUTPUT_DIR + os.environ.get('DNSRECON_OUTPUT_DIR', "scanners/resources/output/dnsrecon/"),

        # The most important wordlists are auto-generated by this software, and are thus output.
        'wordlist_dir': OUTPUT_DIR + os.environ.get('DNSRECON_WORDLIST_DIR', "scanners/resources/wordlists/"),
    },
    'sslscan': {
        # this is beta functionality and not supported in production
        # these are installed system wide and don't require a path (they might when development continues)
        'executable': {
            'Darwin': 'sslscan',
            'Linux': 'sslscan',
        },
        'report_output_dir': OUTPUT_DIR + "scanners/resources/output/sslscan/",
    },
    'openssl': {
        # this is beta functionality and not supported in production
        # these are installed system wide and don't require a path  (they might when development continues)
        'executable': {
            'Darwin': 'openssl',
            'Linux': 'openssl',
        },
    },
    'TLS': {
        # this is beta functionality and not supported in production
        'cve_2016_2107': VENDOR_DIR + 'CVE-2016-2107-padding-oracle/main.go',
        'cve_2016_9244': VENDOR_DIR + 'CVE-2016-9244-ticketbleed/ticketbleed.go',
        'cert_chain_resolver': {
            'Darwin': VENDOR_DIR + 'cert-chain-resolver/cert-chain-resolver-darwin',
            'Linux': VENDOR_DIR + 'cert-chain-resolver/cert-chain-resolver-linux',
        }
    }
}

# Celery 4.0 settings
# Pickle can work, but you need to use certificates to communicate (to verify the right origin)
# It's preferable not to use pickle, yet it's overly convenient as the normal serializer can not
# even serialize dicts.
# http://docs.celeryproject.org/en/latest/userguide/configuration.html
CELERY_accept_content = ['pickle', 'yaml']
CELERY_task_serializer = 'pickle'
CELERY_result_serializer = 'pickle'

# Compression
# Django-compressor is used to compress css and js files in production
# During development this is disabled as it does not provide any feature there
# Django-compressor configuration defaults take care of this.
# https://django-compressor.readthedocs.io/en/latest/usage/
# which plugins to use to find static files
STATICFILES_FINDERS = (
    # default static files finders
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)

COMPRESS_CSS_FILTERS = ['compressor.filters.cssmin.CSSCompressorFilter']

# Slimit doesn't work with vue. Tried two versions. Had to rewrite some other stuff.
# Now using the default, so not explicitly adding that to the settings
# COMPRESS_JS_FILTERS = ['compressor.filters.jsmin.JSMinFilter']

# Brotli compress storage gives some issues.
# This creates the original compressed and a gzipped compressed file.
COMPRESS_STORAGE = (
    'compressor.storage.GzipCompressorFileStorage'
)

# Disable caching during development and production.
# Django only emits caching headers, the webserver/caching-proxy makes sure the rest of the caching is handled.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Enable static file (js/css) compression when not running debug
# https://django-compressor.readthedocs.io/en/latest/settings/#django.conf.settings.COMPRESS_OFFLINE
COMPRESS_OFFLINE = not DEBUG
# https://django-compressor.readthedocs.io/en/latest/settings/#django.conf.settings.COMPRESS_ENABLED
# Enabled when debug is off by default.

# Celery config
CELERY_BROKER_URL = os.environ.get('BROKER', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('RESULT_BACKEND', CELERY_BROKER_URL.replace('amqp://', 'rpc://'))
ENABLE_UTC = True

# Any data transfered with pickle needs to be over tls... you can inject arbitrary objects with
# this stuff... message signing makes it a bit better, not perfect as it peels the onion.
# this stuff... message signing makes it a bit better, not perfect as it peels the onion.
# see: https://blog.nelhage.com/2011/03/exploiting-pickle/
# Yet pickle is the only convenient way of transporting objects without having to lean in all kinds
# of directions to get the job done. Intermediate tables to store results could be an option.
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_TIMEZONE = 'UTC'

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

MAPBOX_TOKEN = "pk.eyJ1IjoibXJmYWlsIiwiYSI6ImNqMHRlNXloczAwMWQyd3FxY3JkMnUxb3EifQ.9nJBaedxrry91O1d90wfuw"

CELERY_BROKER_CONNECTION_MAX_RETRIES = 1
CELERY_BROKER_CONNECTION_RETRY = False

# workaround to try and make rate limited tasks coexist on the same worker as non-rate limited whilst keeping
# good throughput on non-rate limited tasks even though worker interal queue might be plugged with rate limited tasks
CELERY_WORKER_PREFETCH_MULTIPLIER = 0

# numer of tasks to be executed in parallel by celery
CELERY_WORKER_CONCURRENCY = 10

# Settings for statsd metrics collection. Statsd defaults over UDP port 8125.
# https://django-statsd.readthedocs.io/en/latest/#celery-signals-integration
STATSD_HOST = os.environ.get('STATSD_HOST', '127.0.0.1')
STATSD_PREFIX = 'failmap'
# register hooks for selery tasks
STATSD_CELERY_SIGNALS = True
# send database query metric (in production, in development we have debug toolbar for this)
if not DEBUG:
    STATSD_PATCHES = ['django_statsd.patches.db', ]

# enable some features during debug
if DEBUG:
    # enable debug toolbar if available
    try:
        import debug_toolbar

        INSTALLED_APPS.append('debug_toolbar')
        MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware')

        import debug_toolbar.settings

        DEBUG_TOOLBAR_PANELS = [
            'ddt_request_history.panels.request_history.RequestHistoryPanel',
        ] + debug_toolbar.settings.PANELS_DEFAULTS + [
            'django_statsd.panel.StatsdPanel',
        ]
        # send statsd metrics to debug_toolbar
        STATSD_CLIENT = 'django_statsd.clients.toolbar'
    except ImportError:
        pass

# is administrative backend enabled on this instance
ADMIN = bool(APPNAME == 'failmap-admin')

# general email address
MAILTO = 'info@faalkaart.nl'

# if sentry DSN is provided register raven to emit events on exceptions
SENTRY_DSN = os.environ.get('SENTRY_DSN')
if SENTRY_DSN:
    INSTALLED_APPS += ('raven.contrib.django.raven_compat',)
    RAVEN_CONFIG = {
        'dsn': SENTRY_DSN,
        'release': __version__,
    }
    # add sentry ID to request for inclusion in templates
    # https://docs.sentry.io/clients/python/integrations/django/#message-references
    MIDDLEWARE_CLASSES.insert(0, 'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware')

# set javascript sentry token if provided
SENTRY_TOKEN = os.environ.get('SENTRY_TOKEN', '')

SENTRY_ORGANIZATION = 'internet-cleanup-foundation'
SENTRY_PROJECT = 'faalkaart'
SENTRY_PROJECT_URL = 'https://sentry.io/%s/%s' % (SENTRY_ORGANIZATION, SENTRY_PROJECT)

# Some workers or (development) environments don't support both IP networks
# Note that not supporting either protocols can result in all endpoints being killed as they are unreachable by scanners
# We don't check these settings anywhere for sanity as some workers might not need a network at all.
# The defaults stem from our live environment, where we've set IPv4 being present on all containers and workers.
NETWORK_SUPPORTS_IPV4 = os.environ.get('NETWORK_SUPPORTS_IPV4', True)
NETWORK_SUPPORTS_IPV6 = os.environ.get('NETWORK_SUPPORTS_IPV6', False)
