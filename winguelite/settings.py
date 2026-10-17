import os
from pathlib import Path
import environ

# Initialize environ
env = environ.Env(
    DEBUG=(bool, False)
)

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Read .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    
    # Third party apps
    'django_ckeditor_5',
    'crispy_forms',
    'crispy_tailwind',
    'django_filters',
    
    # Local apps
    'core',
    'destinations',
    'itineraries',
    'gallery',
    'blog',
    'testimonials',
    'bookings',
    'contact',
    'cockpit',
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

ROOT_URLCONF = 'winguelite.urls'

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
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'winguelite.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# CKEditor Configuration
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'underline', 'strikethrough', 'code', '|',
            'link', 'bulletedList', 'numberedList', 'todoList', '|',
            'outdent', 'indent', '|',
            'blockQuote', 'insertTable', 'mediaEmbed', '|',
            'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', '|',
            'alignment', '|',
            'undo', 'redo', '|',
            'imageUpload', 'insertImage'
        ],
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'},
                {'model': 'heading4', 'view': 'h4', 'title': 'Heading 4', 'class': 'ck-heading_heading4'},
            ]
        },
        'fontSize': {
            'options': [10, 12, 14, 16, 18, 20, 24, 30]
        },
        'fontColor': {
            'colors': [
                {'color': 'hsl(0, 0%, 0%)', 'label': 'Black'},
                {'color': 'hsl(0, 0%, 30%)', 'label': 'Dim grey'},
                {'color': 'hsl(0, 0%, 60%)', 'label': 'Grey'},
                {'color': 'hsl(0, 75%, 60%)', 'label': 'Red'},
                {'color': 'hsl(30, 75%, 60%)', 'label': 'Orange'},
                {'color': 'hsl(60, 75%, 60%)', 'label': 'Yellow'},
                {'color': 'hsl(90, 75%, 60%)', 'label': 'Light green'},
                {'color': 'hsl(120, 75%, 60%)', 'label': 'Green'},
            ]
        },
        'image': {
            'toolbar': [
                'imageTextAlternative', 'toggleImageCaption', '|',
                'imageStyle:inline', 'imageStyle:block', 'imageStyle:side', '|',
                'linkImage'
            ],
            'upload': {
                'types': ['jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff']
            }
        },
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells']
        },
        'height': 500,
        'width': '100%',
    },
}

# Email Configuration
EMAIL_BACKEND = env('EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_USE_TLS = env('EMAIL_USE_TLS')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
ADMIN_EMAIL = env('ADMIN_EMAIL')
