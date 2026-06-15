import logging

from .base import *  # noqa

DEBUG = True

# Celery: run tasks inline and surface exceptions
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
# Celery 5+ compatible names (no harm if unused)
task_always_eager = True
task_eager_propagates = True

# Never hit real email servers
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

MIDDLEWARE = [
    "querycount.middleware.QueryCountMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "nplusone.ext.django.NPlusOneMiddleware",
] + MIDDLEWARE  # noqa

INSTALLED_APPS += ["querycount", "debug_toolbar", "nplusone.ext.django"]  # noqa

NPLUSONE_LOGGER = logging.getLogger("nplusone")
NPLUSONE_LOG_LEVEL = logging.WARN

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "nplusone": {
            "handlers": ["console"],
            "level": "WARN",
            "propagate": False,
        },
    },
}

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

CSRF_TRUSTED_ORIGINS = [
    "https://api.kitobxonlikharakati.uz",
    "https://dev-api.kitobxonlikharakati.uz",
    "https://*.ngrok-free.app",
]

HOST = "http://localhost:8000"
