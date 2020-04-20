from postfix_adapter.settings.common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '___OBFUSCATED_FOR_MIRRORING___'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {module}[{process:d}:{thread:d}] {levelname} - {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'level': 'INFO'
        },
        'django.db.backends': {
            'level': 'DEBUG'
        }
    }
}

POSTFIX_MAIL_FILE = '___OBFUSCATED_FOR_MIRRORING___'