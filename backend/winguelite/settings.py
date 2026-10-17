from pathlib import Path

import environ

env = environ.Env(DEBUG=(bool, False))

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
REPO_DIR = BASE_DIR.parent

environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Public site URL, used for absolute links in exported content and emails.
SITE_URL = env('SITE_URL', default='https://wingueliteadventures.co.ke').rstrip('/')

# Origins allowed to POST to the form API (the static site's own origin).
CORS_ALLOWED_ORIGINS = env.list(
    'CORS_ALLOWED_ORIGINS',
    default=[SITE_URL, 'http://localhost:4321', 'http://127.0.0.1:4321'],
)
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[SITE_URL])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_ckeditor_5',
    'core',
    'destinations',
    'itineraries',
    'gallery',
    'blog',
    'testimonials',
    'bookings',
    'contact',
    'cockpit',
    'api',
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
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'winguelite.wsgi.application'

# Postgres in production: DATABASE_URL=postgres://user:pass@localhost:5432/dbname
DATABASES = {
    'default': env.db('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
}
DATABASES['default']['CONN_MAX_AGE'] = env.int('DB_CONN_MAX_AGE', default=60)

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = '/admin/login/'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Static site build -------------------------------------------------------
# Content changes in the admin touch this flag; deploy/rebuild.sh (cron) picks it up.
VAR_DIR = BASE_DIR / 'var'
REBUILD_FLAG = VAR_DIR / 'rebuild.flag'
CONTENT_EXPORT_PATH = Path(env('CONTENT_EXPORT_PATH', default=str(REPO_DIR / 'web' / 'src' / 'data' / 'content.json')))
# Built Astro site; Django returns its 404.html for unknown URLs.
STATIC_SITE_DIR = Path(env('STATIC_SITE_DIR', default=str(REPO_DIR / 'web' / 'dist')))
# Responsive WebP renditions generated with Pillow for every content image.
IMAGE_WIDTHS = [480, 960, 1600, 2400]
IMAGE_QUALITY = 78

# --- Security (production) -----------------------------------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
    X_FRAME_OPTIONS = 'SAMEORIGIN'

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

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

CKEDITOR_5_FILE_UPLOAD_PERMISSION = 'staff'

EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='localhost')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default=False)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_TIMEOUT = 15
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='Wingu Elite Adventures <info@wingueliteadventures.co.ke>')
SERVER_EMAIL = DEFAULT_FROM_EMAIL
ADMIN_EMAIL = env('ADMIN_EMAIL', default='info@wingueliteadventures.co.ke')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'WARNING'},
}
