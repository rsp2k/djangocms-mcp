"""
Minimal Django settings for testing djangocms-mcp
"""
import os
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Add the package directory to Python path
package_path = BASE_DIR / 'djangocms_mcp'
if package_path.exists():
    sys.path.insert(0, str(package_path))

# Minimal settings for testing
SECRET_KEY = 'django-insecure-test-key-only-for-testing'
DEBUG = True
ALLOWED_HOSTS = ['*']

# Complete app list for Django CMS testing
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',  # Added for LogEntry model
    'django.contrib.messages',  # Required by Django CMS
    'django.contrib.staticfiles',  # Often needed by CMS
    
    # CMS core (minimal)
    'cms',
    'menus',
    'treebeard',
    
    # Our app
    'djangocms_mcp',
]

# Minimal middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',  # Added for messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageFallbackMiddleware',
]

ROOT_URLCONF = 'tests.urls'

# Minimal template configuration
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
                'django.contrib.messages.context_processors.messages',  # Added for messages
                'cms.context_processors.cms_settings',
            ],
        },
    },
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Use PostgreSQL if DATABASE_URL is provided (for CI)
if 'DATABASE_URL' in os.environ:
    try:
        import dj_database_url
        DATABASES['default'] = dj_database_url.parse(os.environ['DATABASE_URL'])
    except ImportError:
        pass

# Internationalization
LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
]

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Sites framework
SITE_ID = 1

# Django CMS v4 settings
CMS_CONFIRM_VERSION4 = True  # Required for Django CMS v4
CMS_TEMPLATES = [
    ('template_1.html', 'Template One'),
]

CMS_PERMISSION = False  # Disable for simpler testing
CMS_PUBLIC_FOR = 'all'

# Disable migrations for testing
class DisableMigrations:
    def __contains__(self, item):
        return True
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Minimal logging
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

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
