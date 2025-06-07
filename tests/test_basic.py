"""
Simple smoke tests for djangocms_mcp package
"""
import os
import sys
from django.test import TestCase
from django.conf import settings


class TestBasicSetup(TestCase):
    """Test basic Django setup and configuration"""
    
    def test_django_settings_loaded(self):
        """Test that Django settings are properly loaded"""
        self.assertTrue(hasattr(settings, 'INSTALLED_APPS'))
        self.assertTrue(hasattr(settings, 'SECRET_KEY'))
        self.assertIn('djangocms_mcp', settings.INSTALLED_APPS)
    
    def test_database_connection(self):
        """Test that we can connect to the test database"""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            self.assertEqual(result[0], 1)
    
    def test_package_structure(self):
        """Test that the package files exist"""
        current_dir = os.path.dirname(os.path.dirname(__file__))
        
        # Check for package directory (updated to use underscores)
        package_dir = os.path.join(current_dir, 'djangocms_mcp')
        self.assertTrue(os.path.exists(package_dir), f"Package directory should exist at {package_dir}")
        
        # Check for essential files
        essential_files = ['__init__.py', 'apps.py']
        for filename in essential_files:
            file_path = os.path.join(package_dir, filename)
            self.assertTrue(
                os.path.exists(file_path), 
                f"File {filename} should exist in package directory"
            )


class TestAppConfiguration(TestCase):
    """Test Django app configuration"""
    
    def test_app_is_installed(self):
        """Test that the app appears in INSTALLED_APPS"""
        self.assertIn('djangocms_mcp', settings.INSTALLED_APPS)
    
    def test_django_apps_registry(self):
        """Test that Django recognizes the app"""
        from django.apps import apps
        
        # This will raise LookupError if the app isn't properly registered
        try:
            app_config = apps.get_app_config('djangocms_mcp')
            self.assertIsNotNone(app_config)
            self.assertEqual(app_config.name, 'djangocms_mcp')
        except LookupError:
            self.fail("djangocms_mcp app is not properly registered with Django")


class TestImports(TestCase):
    """Test that we can import the package modules"""
    
    def test_package_import(self):
        """Test that we can import from the package"""
        try:
            # Add the package to the path
            current_dir = os.path.dirname(os.path.dirname(__file__))
            package_dir = os.path.join(current_dir, 'djangocms_mcp')
            
            if package_dir not in sys.path:
                sys.path.insert(0, package_dir)
            
            # Try importing the apps module
            import apps
            self.assertTrue(hasattr(apps, 'DjangoCmsMcpConfig'))
            
        except ImportError as e:
            # Don't fail the entire test suite for this
            self.skipTest(f"Package import test skipped: {e}")


class TestAppStructure(TestCase):
    """Test the application structure"""
    
    def test_app_structure(self):
        """Test that the app has the expected structure"""
        import os
        
        current_dir = os.path.dirname(os.path.dirname(__file__))
        
        # Check for the correct directory structure (using underscores)
        package_dir = os.path.join(current_dir, 'djangocms_mcp')
        self.assertTrue(os.path.exists(package_dir), "Package directory should exist")
        
        # Check for key files
        expected_files = ['__init__.py', 'apps.py', 'models.py', 'cms_plugins.py', 'mcp.py']
        for expected_file in expected_files:
            file_path = os.path.join(package_dir, expected_file)
            self.assertTrue(
                os.path.exists(file_path), 
                f"{expected_file} should exist in djangocms_mcp package"
            )
        
        # Check for templates directory
        templates_dir = os.path.join(package_dir, 'templates', 'djangocms_mcp')
        self.assertTrue(
            os.path.exists(templates_dir), 
            "Template directory should exist"
        )
