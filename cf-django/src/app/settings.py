"""Settings for running the Infinite Care Django project on Cloudflare Python Workers."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent           # cf-django/src
SITE_ROOT = BASE_DIR.parent.parent                          # repo root (only used at build time)
CI = os.getenv("WORKERS_CI") == "1"


def env_list(name, default=""):
    return [x.strip() for x in os.getenv(name, default).split(",") if x.strip()]


SECRET_KEY = os.getenv("SECRET_KEY") or ("build-only" if CI else None)
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY secret missing")
DEBUG = False
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "*")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")
CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS")
CORS_URLS_REGEX = r"^/api/.*$"

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "content", "contact", "cfmedia",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "app.cors.SimpleCorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "app.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "app.wsgi.application"
DATABASES = {} if CI else {"default": {"ENGINE": "django_cf.db.backends.do"}}
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

LANGUAGE_CODE = "en"
TIME_ZONE = "Europe/Budapest"
USE_I18N = True
USE_TZ = True
SITE_LANGUAGES = ("en", "hu")

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR.parent / "staticfiles" / "static"
STATICFILES_DIRS = [("css", SITE_ROOT / "css"), ("js", SITE_ROOT / "js"), ("assets", SITE_ROOT / "assets")] if CI else []
# Uploaded images are stored as blobs in the database (no R2 needed); seeded images point to static assets
STORAGES = {
    "default": {"BACKEND": "cfmedia.storage.DatabaseStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
MEDIA_URL = "/media/"
MEDIA_ROOT = "/tmp/media"
CONTENT_SEED_FILES = False
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SILENCED_SYSTEM_CHECKS = ["fields.E210"]  # Pillow not bundled; images validated by extension only

CONTACT_RATE_LIMIT = 5
CONTACT_RATE_WINDOW = 900
TRUST_X_FORWARDED_FOR = False
TRUST_CF_CONNECTING_IP = True
NOTIFY_EMAIL = ""
EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@infinitecare.hu"
STATIC_EXPORT_API_URL = ""
STATIC_EXPORT_SITE_URL = "https://infinitecare-api.amyrsalarr.workers.dev/"
MGMT_TOKEN = os.getenv("MGMT_TOKEN", "")
PASSWORD_HASHERS = ["app.hashers.PurePythonPBKDF2Hasher"]
LOGGING = {"version": 1, "disable_existing_loggers": False,
           "handlers": {"console": {"class": "logging.StreamHandler"}},
           "loggers": {"django.request": {"handlers": ["console"], "level": "ERROR"}}}
