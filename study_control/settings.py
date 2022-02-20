import os
from filebrowser import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '05b#v0*)x6!fha^(67ewgmsw+jm19z*n2q6%_my(*&c0ku+dsl'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'tinymce',
    'filebrowser',
    "grappelli",
    'control',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',

]
CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'study_control.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'study_control.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

LOGIN_REDIRECT_URL = '/'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

X_FRAME_OPTIONS = 'SAMEORIGIN'

FILEBROWSER_DIRECTORY = getattr(settings, "FILEBROWSER_DIRECTORY", 'uploads/')


TINYMCE_DEFAULT_CONFIG = {
    'plugins': '''
            textcolor link image media preview codesample contextmenu
            table code lists insertdatetime  contextmenu directionality visualblocks
            visualchars code autolink lists charmap hr

            ''',
    'toolbar1': '''
            bold italic underline | fontselect,
            fontsizeselect  | forecolor | alignleft  
            aligncenter alignright alignjustify | bullist numlist table |
            | link image media |
            ''',

    'contextmenu': 'formats | link image',
    'menubar': False,
    'statusbar': True,
    'height': 500,
}

LOGIN_URL = '/login'

MAX_FILE_SIZE = 5

FILE_CHOISE_EXTENSIONS = (
    ('1', "Все типы файлов"),
    ('2', "Изображения"),
    ('3', "Документы"),
)

EXTENSIONS = {
    '1': ["*", ],

    '2': ['png', 'avif', 'gif', 'jpg', 'jpeg', 'jfif', 'pjpeg', 'pjp',
          'png', 'svg', 'webp', 'bmp', 'ico', 'cur', 'tif', 'tiff', ],

    '3': ['doc', 'docx', 'txt', 'ppt', 'pptx', 'odt', 'pdf', 'xls', 'xlsx'],
}
