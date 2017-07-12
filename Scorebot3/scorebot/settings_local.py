import os
import scorebot.utils.logger


DEBUG = True
USE_TZ = True
USE_I18N = True
USE_L10N = True
TIME_ZONE = 'UTC'
APPEND_SLASH = False
ALLOWED_HOSTS = ['*']
LANGUAGE_CODE = 'en-us'
STATIC_URL = '/static/'
SBE_VERSION = 'v3.1beta'
ROOT_URLCONF = 'scorebot.urls'
LOG_FILE = '/tmp/scorebot.log'
WSGI_APPLICATION = 'scorebot.wsgi.application'
SECRET_KEY = 'mvn+$y(2lz%!nga3h@p7jf*zsrop^(ojp1)=mdn1gz+im-c%re'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN_DIR = os.path.join(BASE_DIR, 'plugins')
DAEMON_DIR = os.path.join(BASE_DIR, 'scorebot', 'utils', 'daemons')
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
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]
scorebot.utils.logger.init_simple(LOG_FILE, 'DEBUG')
