"""Django settings for the Infinite Care site. All deploy-specific values come from env / backend/.env."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent          # backend/
SITE_ROOT = BASE_DIR.parent                                # repo root (static site: css/, js/, assets/)
load_dotenv(BASE_DIR / '.env')


def env_list(name, default=''):
    return [x.strip() for x in os.getenv(name, default).split(',') if x.strip()]


DEBUG = os.getenv('DEBUG', 'False').lower() in ('1', 'true', 'yes')
SECRET_KEY = os.getenv('SECRET_KEY') or ('dev-insecure-key' if DEBUG else None)
if not SECRET_KEY:
    raise RuntimeError('Set SECRET_KEY in backend/.env (or DEBUG=True for local development)')
ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', 'localhost,127.0.0.1')
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'corsheaders',
    'content',
    'contact',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]
WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': Path(os.getenv('SQLITE_PATH', BASE_DIR / 'db.sqlite3')),
}}
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}

AUTH_PASSWORD_VALIDATORS = [{'NAME': f'django.contrib.auth.password_validation.{v}'} for v in
                            ('UserAttributeSimilarityValidator', 'MinimumLengthValidator',
                             'CommonPasswordValidator', 'NumericPasswordValidator')]

LANGUAGE_CODE = 'en'
TIME_ZONE = os.getenv('TIME_ZONE', 'Europe/Budapest')
USE_I18N = True
USE_TZ = True
SITE_LANGUAGES = ('en', 'hu')

# Static: the site's own css/js/assets folders are served at /static/... by WhiteNoise
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [('css', SITE_ROOT / 'css'), ('js', SITE_ROOT / 'js'), ('assets', SITE_ROOT / 'assets')]
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
}
MEDIA_URL = '/media/'
MEDIA_ROOT = Path(os.getenv('MEDIA_ROOT', BASE_DIR / 'media'))
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# CORS (only the public API) – e.g. the GitHub Pages copy of the site
CORS_ALLOWED_ORIGINS = env_list('CORS_ALLOWED_ORIGINS', 'https://amirsalarrabaniha.github.io')
CORS_URLS_REGEX = r'^/api/.*$'

# Contact form
CONTACT_RATE_LIMIT = int(os.getenv('CONTACT_RATE_LIMIT', '5'))          # submissions …
CONTACT_RATE_WINDOW = int(os.getenv('CONTACT_RATE_WINDOW', '900'))      # … per N seconds per IP
NOTIFY_EMAIL = os.getenv('NOTIFY_EMAIL', '')                            # empty = no e-mail notification
# Behind a proxy (Render/Railway/nginx) trust X-Forwarded-For for rate limiting
TRUST_X_FORWARDED_FOR = os.getenv('TRUST_X_FORWARDED_FOR', 'False').lower() in ('1', 'true', 'yes')

EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('1', 'true', 'yes')
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() in ('1', 'true', 'yes')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Infinite Care website <no-reply@infinitecare.hu>')
EMAIL_BACKEND = ('django.core.mail.backends.smtp.EmailBackend' if EMAIL_HOST
                 else 'django.core.mail.backends.console.EmailBackend')

# Static export (GitHub Pages fallback): API URL baked into exported pages ('' = mailto fallback)
STATIC_EXPORT_API_URL = os.getenv('STATIC_EXPORT_API_URL', '')
STATIC_EXPORT_SITE_URL = os.getenv('STATIC_EXPORT_SITE_URL', 'https://amirsalarrabaniha.github.io/infinitecare-site/')

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = os.getenv('SECURE_COOKIES', 'True').lower() in ('1', 'true', 'yes')
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'SAMEORIGIN'

LOGGING = {'version': 1, 'disable_existing_loggers': False,
           'handlers': {'console': {'class': 'logging.StreamHandler'}},
           'root': {'handlers': ['console'], 'level': 'INFO'}}
