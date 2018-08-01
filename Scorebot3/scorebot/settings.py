import os

from scorebot.utils.logger import log_init

DEBUG = True
USE_TZ = True
USE_I18N = True
USE_L10N = True
TIME_ZONE = 'UTC'
DUMP_DATA = True
TWITTER_API = {
    'ENABLED': True,
    'CONSUMER_KEY': '',
    'ACCESS_TOKEN': '',
    'CONSUMER_SECRET': '',
    'ACCESS_TOKEN_SECRET': '',
}
APPEND_SLASH = False
SBE_VERSION = 'v3.3.4'
MEDIA_URL = '/upload/'
ALLOWED_HOSTS = ['*']
LANGUAGE_CODE = 'en-us'
STATIC_URL = '/static/'
LOG_DIR = '/tmp/scorebot3'
ROOT_URLCONF = 'scorebot.urls'
DUMP_DIR = '/tmp/scorebot3_dumps'
MEDIA_ROOT = '/home/scorebot3/logos'
WSGI_APPLICATION = 'scorebot.wsgi.application'
SECRET_KEY = 'mvn+$y(2lz%!nga3h@p7jf*zsrop^(ojp1)=mdn1gz+im-c%re'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN_DIR = os.path.join(BASE_DIR, 'scorebot_assets', 'plugins')
DAEMON_DIR = os.path.join(BASE_DIR, 'scorebot_assets', 'daemons')
STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'scorebot_static'),
        ]
log_init(LOG_DIR, 'DEBUG')
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'scorebot_core',
    'scorebot_grid',
    'scorebot_game',
    'scorebot_api',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'scorebot_html')],
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
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '',
        'HOST': '',
        'USER': '',
        'PASSWORD': '',
    }
}
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]
