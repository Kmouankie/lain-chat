import environ
from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent


env = environ.Env(
    DEBUG=(bool, False)
)

environ.Env.read_env(os.path.join(BASE_DIR.parent, '.env'))


SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
   
    'channels',  
    'corsheaders',
    'csp',
    
    
    'security',          
    'anonymization',    
    'users',
    'chat',
    'wired',
    'authentication',
]


SECURITY_MIDDLEWARE = [
    'security.middleware.AdvancedSecurityMiddleware',
    'security.middleware.RequestSanitizationMiddleware',
    'security.middleware.AnonymizationMiddleware',
    'security.middleware.LayerIsolationMiddleware',
]


MIDDLEWARE = SECURITY_MIDDLEWARE + [
    'corsheaders.middleware.CorsMiddleware',
    #'csp.middleware.CSPMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lain_chat.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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


ASGI_APPLICATION = 'lain_chat.asgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'lain_chat.sqlite3',
    },
    'anonymous_mapping': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'lain_anonymous.sqlite3',
    },
}

#  PostgreSQL (pour plus tard)
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lain_chat',
        'USER': 'lain_user',
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'prefer',
        },
    },
    'anonymous_mapping': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lain_anonymous',
        'USER': 'lain_user', 
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'prefer',
        },
    },
}
"""


CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
        'CONFIG': {
            'capacity': 1500,  
            'expiry': 60,      
        },
    }
}

# Configuration Redis (pour plus tard)
"""
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('localhost', 6379)],
        },
    },
}
"""


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'lain-cache',
        'TIMEOUT': 300, 
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}


"""
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
"""


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTH_USER_MODEL = 'users.MinimalUser'




SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = 'no-referrer'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'


CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_USE_SESSIONS = True
CSRF_COOKIE_NAME = 'csrftoken_lain'


SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 3600  # 1 heure
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_NAME = 'sessionid_lain'


X_FRAME_OPTIONS = 'DENY'


CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_CREDENTIALS = True

# Content Security Policy 
#CSP_DEFAULT_SRC = ("'self'",)
#CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com")
#CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
#CSP_IMG_SRC = ("'self'", "data:")
#CSP_CONNECT_SRC = ("'self'", "ws:", "wss:")
#CSP_FONT_SRC = ("'self'",)
#CSP_OBJECT_SRC = ("'none'",)
#CSP_BASE_URI = ("'self'",)
#CSP_FORM_ACTION = ("'self'",)
#CSP_FRAME_ANCESTORS = ("'none'",)


DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440  
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440 
DATA_UPLOAD_MAX_NUMBER_FIELDS = 100


EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = 'noreply@lain-project.local'


if not DEBUG:
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost'] + env.list('ALLOWED_HOSTS', default=[])
else:
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '*'] 


CONN_MAX_AGE = 60  
SILENCED_SYSTEM_CHECKS = []  


LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'secure': {
            'format': '{asctime} {levelname} {name} {message}',
            'style': '{',
        },
        'anonymous': {
            'format': '[{asctime}] {levelname} - ANONYMOUS_EVENT - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'security_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'security.log',
            'formatter': 'secure',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'secure',
        },
        'anonymous_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'lain_anonymous.log',
            'formatter': 'anonymous',
        },
    },
    'loggers': {
        'lain_security': {
            'handlers': ['security_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'lain_websocket_security': {
            'handlers': ['security_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'lain_consumer': {
            'handlers': ['security_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'lain_models': {
            'handlers': ['security_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'anonymization': {
            'handlers': ['anonymous_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'channels': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        'security': {
            'handlers': ['security_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


if DEBUG:
    
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    
    
    LOGGING['loggers']['lain_security']['level'] = 'DEBUG'
    LOGGING['loggers']['lain_websocket_security']['level'] = 'DEBUG'


ANONYMIZATION_CONFIG = {
    'ENABLED': env.bool('ANONYMIZATION_ENABLED', True),
    'ZERO_KNOWLEDGE_AUTH': env.bool('ZERO_KNOWLEDGE_AUTH', True),
    'LAYER_ROTATION_HOURS': env.int('AUTO_LAYER_ROTATION_HOURS', 24),
    'MESSAGE_RETENTION_DAYS': 7,
    'KEY_ROTATION_HOURS': 6,
    'IP_LOGGING': False,
    'METADATA_STRIPPING': True,
    'EMERGENCY_BURN_ENABLED': env.bool('EMERGENCY_BURN_ENABLED', True),
    'FRAGMENTATION_DEPTH': 5,
    'EPHEMERAL_MODE_DEFAULT': False,
    'WEBSOCKET_ANONYMIZATION': True,
    'MAX_LAYERS': 5,
    'AUTO_BURN_INACTIVE_HOURS': 24,
   
    'RATE_LIMITING_ENABLED': True,
    'ATTACK_DETECTION_ENABLED': True,
    'ADVANCED_HEADERS_ENABLED': True,
    'INPUT_SANITIZATION_ENABLED': True,
}


ENCRYPTION_CONFIG = {
    'MASTER_KEY': env('ENCRYPTION_MASTER_KEY', default=''),
    'LAYER_SALT_KEY': env('LAYER_SALT_KEY', default=''),
    'FRAGMENT_KEY': env('FRAGMENT_ENCRYPTION_KEY', default=''),
}


if not DEBUG:
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', SECRET_KEY)
    if not os.environ.get('DJANGO_SECRET_KEY'):
        import secrets
        print("WARNING: Generating temporary secret key. Set DJANGO_SECRET_KEY in production!")
        SECRET_KEY = secrets.token_urlsafe(50)