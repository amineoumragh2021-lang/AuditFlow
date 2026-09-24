from pathlib import Path
import os

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

ON_VERCEL = os.environ.get('VERCEL') == '1'
if not ON_VERCEL:
    # Explicit process variables win, then .env.local, then .env.
    load_dotenv(BASE_DIR / '.env.local', override=False)
    load_dotenv(BASE_DIR / '.env', override=False)


def env_list(name):
    return [value.strip() for value in os.environ.get(name, '').split(',') if value.strip()]


debug_value = os.environ.get('DEBUG', 'False').strip().lower()
if debug_value not in {'true', 'false', '1', '0'}:
    raise ImproperlyConfigured('DEBUG must be True, False, 1 or 0.')
DEBUG = debug_value in {'true', '1'}
if ON_VERCEL and DEBUG:
    raise ImproperlyConfigured('DEBUG must be False on Vercel.')

SECRET_KEY = os.environ.get('SECRET_KEY', '')
if not SECRET_KEY:
    raise ImproperlyConfigured('Set SECRET_KEY in the environment or your local .env file.')
if not DEBUG and (len(SECRET_KEY) < 50 or SECRET_KEY.startswith('django-insecure-')):
    raise ImproperlyConfigured('Production requires a new random SECRET_KEY of at least 50 characters.')

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS')
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS')
if DEBUG:
    ALLOWED_HOSTS += ['127.0.0.1', 'localhost', '[::1]']
    CSRF_TRUSTED_ORIGINS += ['http://127.0.0.1:8000', 'http://localhost:8000']
if ON_VERCEL:
    # Exact deployment / branch / production hosts, never all *.vercel.app tenants.
    for name in ('VERCEL_URL', 'VERCEL_BRANCH_URL', 'VERCEL_PROJECT_PRODUCTION_URL'):
        host = os.environ.get(name, '').strip()
        if host:
            ALLOWED_HOSTS.append(host)
            CSRF_TRUSTED_ORIGINS.append(f'https://{host}')
ALLOWED_HOSTS = list(dict.fromkeys(ALLOWED_HOSTS))
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(CSRF_TRUSTED_ORIGINS))
if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured('Set ALLOWED_HOSTS to the exact public hostname(s).')

CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'
SECURE_SSL_REDIRECT = not DEBUG
if ON_VERCEL:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'audit',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

database_url = os.environ.get('DATABASE_URL', '').strip()
if database_url:
    if not database_url.startswith(('postgres://', 'postgresql://')):
        raise ImproperlyConfigured('DATABASE_URL must be a PostgreSQL URL; leave it empty for local SQLite.')
    DATABASES = {'default': dj_database_url.parse(database_url, conn_max_age=0)}
    # Safe with Neon's transaction pooler; no server-side cursors or prepared statements.
    DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True
    DATABASES['default'].setdefault('OPTIONS', {})['prepare_threshold'] = None
    DATABASES['default']['OPTIONS'].setdefault('connect_timeout', 10)
    if ON_VERCEL:
        DATABASES['default']['OPTIONS']['sslmode'] = 'require'
elif ON_VERCEL:
    raise ImproperlyConfigured('DATABASE_URL is required on Vercel: AuditFlow writes accounts, sessions and audit data.')
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'Africa/Casablanca'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Documents are served only by the authenticated download view.
MEDIA_ROOT = BASE_DIR / 'private_uploads'

storage_variables = (
    'AWS_STORAGE_BUCKET_NAME', 'AWS_S3_ENDPOINT_URL', 'AWS_S3_REGION_NAME',
    'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY',
)
if ON_VERCEL or any(os.environ.get(name) for name in storage_variables):
    missing = [name for name in storage_variables if not os.environ.get(name)]
    if missing:
        raise ImproperlyConfigured('Persistent private document storage requires: ' + ', '.join(missing))
    if not os.environ['AWS_S3_ENDPOINT_URL'].startswith('https://'):
        raise ImproperlyConfigured('AWS_S3_ENDPOINT_URL must use HTTPS.')
    STORAGES['default'] = {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {
            'bucket_name': os.environ['AWS_STORAGE_BUCKET_NAME'],
            'endpoint_url': os.environ['AWS_S3_ENDPOINT_URL'],
            'region_name': os.environ['AWS_S3_REGION_NAME'],
            'access_key': os.environ['AWS_ACCESS_KEY_ID'],
            'secret_key': os.environ['AWS_SECRET_ACCESS_KEY'],
            'default_acl': None,
            'file_overwrite': False,
            'querystring_auth': True,
            'signature_version': 's3v4',
            'addressing_style': 'path',
            'max_memory_size': 1024 * 1024,
        },
    }

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
