import os

from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS.append(".appengine.com")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
assert SECRET_KEY, "DJANGO_SECRET_KEY environment variable must be set"

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Database
db_config = os.getenv("DB_CONFIG")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": db_config["DB_NAME"],
        "USER": db_config["DB_USER"],
        "PASSWORD": db_config["DB_PASS"],
        "HOST": db_config["DB_HOST"],
        "PORT": "5432",
    }
}

SILENCED_SYSTEM_CHECKS = [
    "security.W004",  # SECURE_HSTS_SECONDS
    "security.W008",  # SECURE_SSL_REDIRECT
]
