from decouple import config
import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-your-secret-key')
DEBUG = config('DEBUG', default=True, cast=bool)
# ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost').split(',')

# --- Application definition ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd Party Apps
    'rest_framework',
    'rest_framework.authtoken', # dj-rest-auth ต้องการ
    'corsheaders',
    'api.apps.ApiConfig', # Local Apps

    # --- เพิ่ม Apps สำหรับ Google Login ---
    'dj_rest_auth',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth.registration',
    'allauth.socialaccount.providers.google',
]

# --- เพิ่ม SITE_ID (จำเป็นสำหรับ allauth) ---
SITE_ID = 1

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware', # สำหรับ Django Templates (API ไม่จำเป็น)
]

ROOT_URLCONF = 'phishing_detector.urls'

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

WSGI_APPLICATION = 'phishing_detector.wsgi.application'

# --- Database ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='phishing_detector'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# --- Password validation ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# --- Internationalization ---
LANGUAGE_CODE = 'th'
TIME_ZONE = 'Asia/Bangkok'
USE_I18N = True
USE_TZ = True

# --- Static files (CSS, JavaScript, Images) ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- การตั้งค่าที่แก้ไขและเพิ่มเข้ามา ---

# 1. Django Rest Framework และ Simple JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# 2. CORS Headers
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",  # URL ของ React App (Default)
#     "http://127.0.0.1:3000",
#     "http://localhost:5173",  # URL ของ React App (Vite)
#     "http://127.0.0.1:5173",
# ]
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000,http://127.0.0.1:3000').split(',')

CORS_ALLOW_CREDENTIALS = True  # สำคัญ! สำหรับ JWT และ Cookie
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

#  ถ้าอยู่บน Production ให้ปิด CSRF สำหรับ API
if not DEBUG:
    CSRF_TRUSTED_ORIGINS = [
        'https://phishing-frontend-tutj.onrender.com',
    ]
# --- ตั้งค่าส่วนของ dj-rest-auth และ allauth ---

# 3. ระบุ Authentication Backends
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# 4. ตั้งค่าให้ dj-rest-auth ใช้ Simple JWT
REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_HTTPONLY': False, # ตั้งเป็น False เพื่อให้ Token ถูกส่งกลับมาใน body
}

# 5. ตั้งค่า allauth
ACCOUNT_EMAIL_VERIFICATION = 'none' # ไม่ต้องยืนยันอีเมลซ้ำซ้อน
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False # ให้ใช้อีเมลเป็นหลักในการ Login

# 6. ตั้งค่า Google Provider
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID'), 
            'secret': config('GOOGLE_CLIENT_SECRET'), 
            'key': ''
        }
    }
}