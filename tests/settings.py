"""
Django settings for testing djangocms-mcp
"""
import os
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Add the package directory to Python path so we can import it
# Handle both "djangocms-mcp" and "djangocms_mcp" directory names
possible_paths = [
    BASE_DIR / 'djangocms-mcp',
    BASE_DIR / 'djangocms_mcp',
]

for path in possible_paths:
    if path.exists():
        sys.path.insert(0, str(path))
        break

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-test-key-only-for-testing'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # CMS dependencies
    'cms',
    'menus',
    'treebeard',
    'djangocms_text_ckeditor',
    'filer',
    'easy_thumbnails',
    
    # MCP - try both possible app names
    'djangocms_mcp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageFallbackMiddleware',
]

ROOT_URLCONF = 'tests.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'tests' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'cms.context_processors.cms_settings',
            ],
        },
    },
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'tests' / 'db.sqlite3',
    }
}

# Use PostgreSQL if DATABASE_URL is provided (for CI)
if 'DATABASE_URL' in os.environ:
    try:
        import dj_database_url
        DATABASES['default'] = dj_database_url.parse(os.environ['DATABASE_URL'])
    except ImportError:
        # Fall back to sqlite if dj_database_url is not available
        pass

# Internationalization
LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('de', 'German'),
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Sites framework
SITE_ID = 1

# Django CMS settings
CMS_TEMPLATES = [
    ('template_1.html', 'Template One'),
]

CMS_PLACEHOLDER_CONF = {}

CMS_PERMISSION = True
CMS_PUBLIC_FOR = 'all'
CMS_CACHE_DURATIONS = {
    'content': 60,
    'menus': 3600,
    'permissions': 3600,
}

# Easy thumbnails
THUMBNAIL_PROCESSORS = [
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop', 
    'easy_thumbnails.processors.scale_and_crop',
    'easy_thumbnails.processors.filters',
]

# Test settings
if 'test' in os.environ.get('DJANGO_SETTINGS_MODULE', '') or 'pytest' in sys.modules:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
    
    # Disable migrations for faster tests
    class DisableMigrations:
        def __contains__(self, item):
            return True
        def __getitem__(self, item):
            return None
    
    MIGRATION_MODULES = DisableMigrations()
    
    # Simplify logging for tests
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'null': {
                'class': 'logging.NullHandler',
            },
        },
        'root': {
            'handlers': ['null'],
        },
    }
    
    # Skip some CMS dependencies if not available
    try:
        import djangocms_text_ckeditor
    except ImportError:
        INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'djangocms_text_ckeditor']
    
    try:
        import filer
    except ImportError:
        INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'filer']
        
    try:
        import easy_thumbnails
    except ImportError:
        INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'easy_thumbnails']
