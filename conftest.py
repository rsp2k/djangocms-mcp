"""
Test configuration for djangocms-mcp
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def pytest_configure():
    """Configure Django for pytest"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
    
    # Configure Django if not already configured
    if not settings.configured:
        django.setup()

def pytest_unconfigure():
    """Clean up after pytest"""
    pass
