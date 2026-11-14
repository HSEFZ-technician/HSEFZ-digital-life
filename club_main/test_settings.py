"""Settings for the pytest suite: in-memory SQLite, no external services."""
from club_main.settings import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
CELERY_TASK_ALWAYS_EAGER = True
DEBUG = False
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']
