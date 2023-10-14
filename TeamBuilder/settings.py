"""
Django settings for TeamBuilder project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
# import django_heroku

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-klg$qd#!@a+%^=vq-g7gy0vsme$dlf@r9d9gsnge$6k8e+7@i4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost','0.0.0.0','127.0.0.1','djparida.pythonanywhere.com','teamsbuilders.com','www.teamsbuilders.com','3.108.238.214','10.0.2.2','192.168.138.212','192.168.29.53']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'ecomApp',
    'django_filters',
    'rest_framework.authtoken',
    'vestige',
    'teamsbuilders',
    'hhi',
    'amulyaHerbal',
    'proteinWorld'
]

AUTH_USER_MODEL = 'ecomApp.User'

CORS_EXPOSE_HEADERS = (
'Access-Control-Allow-Origin: *',
)
CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_WHITELIST  = [
#     "http://localhost:8080",
# ]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware'
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler'
}

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


ROOT_URLCONF = 'TeamBuilder.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'dist'),
            os.path.join(BASE_DIR, 'hhi/templates/')
        ],
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

WSGI_APPLICATION = 'TeamBuilder.wsgi.application'
CSRF_COOKIE_NAME = "XSRF-TOKEN"

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'djongo',
#         'CLIENT': {
#             "host":"mongodb+srv://djpkanha:123qwe..@cluster0.jcpma.mongodb.net/TeamBuilder?retryWrites=true&w=majority",
#             "name":"TeamBuilder",
#             'authMechanism': 'SCRAM-SHA-1'
#         }
#     }
# }
# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'teamsbuilders',
        'USER': 'djparida',
        'PASSWORD': '123qwe..',
        'HOST': '3.108.238.214',
        'PORT': '',
    }
}


# DATABASES = {
#      'default': {
#          'ENGINE': 'django.db.backends.mysql',
#          'NAME': 'djparida$teamsbuilder',
#          'USER': 'djparida',
#          'PASSWORD': '123qwe..',
#          'HOST': 'djparida.mysql.pythonanywhere-services.com',
#          'PORT': '3306'
#      }
# }
# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata' #indian timezone

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = 'argon-dashboard-react/static/'
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'dist/static'),
#     os.path.join(BASE_DIR, 'ecomApp/static')
# ]
STATIC_ROOT = os.path.join(BASE_DIR, 'dist/static/')

# STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'ecomApp/static')


# STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# MEDIA_URL = '/img/'
# MEDIA_ROOT  = os.path.join(BASE_DIR, 'dist/img/')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'ecomApp/media/')

MEDIA_URL = 'vestige/media/'
MEDIA_ROOT_V = os.path.join(BASE_DIR, 'vestige/media/')

MEDIA_URL = 'hhi/media/'
MEDIA_ROOT_H = os.path.join(BASE_DIR, 'hhi/media/')

MEDIA_URL = 'proteinWorld/media/'
MEDIA_ROOT_P = os.path.join(BASE_DIR, 'proteinWorld/media/')

MEDIA_URL = 'amulyaHerbal/media/'
MEDIA_ROOT_A = os.path.join(BASE_DIR, 'amulyaHerbal/media/')
# django_heroku.settings(locals())
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#AWS

AWS_ACCESS_KEY_ID = 'AKIAXZ2QG3Q2BFTMD5LI'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'teamsbuilders'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_ADDRESSING_STYLE = 'virtual'
AWS_S3_REGION_NAME = 'ap-south-1'
AWS_S3_FILE_OVERWRITE = True
AWS_DEFAULT_ACL = None
AWS_S3_VERIFY = True
AWS_QUERYSTRING_AUTH = False
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage' 
DATA_UPLOAD_MAX_MEMORY_SIZE = 7242880