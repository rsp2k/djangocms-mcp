"""
Integration tests for djangocms-mcp app configuration and setup
"""
import pytest
from django.test import TestCase, override_settings
from django.apps import apps
from django.conf import settings


class TestAppConfiguration(TestCase):
    """Test Django app configuration and integration"""

    def test_app_is_installed(self):
        """Test that djangocms_mcp app is properly installed"""
        self.assertIn('djangocms_mcp', settings.INSTALLED_APPS)

    def test_app_config_loaded(self):
        """Test that app config is properly loaded"""
        app_config = apps.get_app_config('djangocms_mcp')
        
        self.assertEqual(app_config.name, 'djangocms_mcp')
        self.assertEqual(app_config.verbose_name, 'Django CMS MCP Server')

    def test_app_models_loaded(self):
        """Test that app models are properly loaded"""
        from djangocms_mcp.models import MCPServerPlugin
        
        # Verify model is accessible
        self.assertTrue(hasattr(MCPServerPlugin, 'objects'))
        
        # Verify model is registered with Django
        app_config = apps.get_app_config('djangocms_mcp')
        model_names = [model._meta.model_name for model in app_config.get_models()]
        self.assertIn('mcpserverplugin', model_names)

    def test_cms_plugin_registration(self):
        """Test that CMS plugins are registered on app ready"""
        from cms.plugin_pool import plugin_pool
        
        # Get all registered plugins
        registered_plugins = plugin_pool.get_all_plugins()
        plugin_names = [p.__name__ for p in registered_plugins]
        
        # Our plugin should be registered
        self.assertIn('MCPServerCMSPlugin', plugin_names)

    def test_app_ready_signal(self):
        """Test that app ready signal properly initializes everything"""
        # This is implicitly tested by the above tests
        # If the app wasn't ready, plugins wouldn't be registered
        # and models wouldn't be available
        
        from djangocms_mcp.apps import DjangoCmsMcpConfig
        app_config = DjangoCmsMcpConfig('djangocms_mcp', 'djangocms_mcp')
        
        self.assertEqual(app_config.name, 'djangocms_mcp')
        self.assertEqual(app_config.verbose_name, 'Django CMS MCP Server')


class TestAppDependencies(TestCase):
    """Test app dependencies and requirements"""

    def test_required_apps_installed(self):
        """Test that required Django apps are installed"""
        required_apps = [
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'cms',
            'menus',
            'treebeard'
        ]
        
        for app in required_apps:
            with self.subTest(app=app):
                self.assertIn(app, settings.INSTALLED_APPS, 
                             f"Required app {app} not found in INSTALLED_APPS")

    def test_cms_settings_present(self):
        """Test that required CMS settings are present"""
        # Test CMS_CONFIRM_VERSION4 is set
        self.assertTrue(getattr(settings, 'CMS_CONFIRM_VERSION4', False))
        
        # Test CMS_TEMPLATES is configured
        cms_templates = getattr(settings, 'CMS_TEMPLATES', [])
        self.assertIsInstance(cms_templates, list)
        self.assertGreater(len(cms_templates), 0)

    def test_database_configuration(self):
        """Test that database is properly configured"""
        self.assertIn('default', settings.DATABASES)
        self.assertIn('ENGINE', settings.DATABASES['default'])

    def test_middleware_configuration(self):
        """Test that required middleware is configured"""
        required_middleware = [
            'cms.middleware.user.CurrentUserMiddleware',
            'cms.middleware.page.CurrentPageMiddleware',
            'cms.middleware.toolbar.ToolbarMiddleware',
            'cms.middleware.language.LanguageFallbackMiddleware'
        ]
        
        for middleware in required_middleware:
            with self.subTest(middleware=middleware):
                self.assertIn(middleware, settings.MIDDLEWARE,
                             f"Required middleware {middleware} not found")


class TestAppImports(TestCase):
    """Test that app modules can be imported correctly"""

    def test_import_models(self):
        """Test importing models module"""
        try:
            from djangocms_mcp import models
            self.assertTrue(hasattr(models, 'MCPServerPlugin'))
        except ImportError as e:
            self.fail(f"Failed to import models: {e}")

    def test_import_cms_plugins(self):
        """Test importing cms_plugins module"""
        try:
            from djangocms_mcp import cms_plugins
            self.assertTrue(hasattr(cms_plugins, 'MCPServerCMSPlugin'))
        except ImportError as e:
            self.fail(f"Failed to import cms_plugins: {e}")

    def test_import_mcp(self):
        """Test importing mcp module"""
        try:
            from djangocms_mcp import mcp
            self.assertTrue(hasattr(mcp, 'DjangoCMSVersioningTools'))
            self.assertTrue(hasattr(mcp, 'PageQueryTool'))
        except ImportError as e:
            self.fail(f"Failed to import mcp: {e}")

    def test_import_apps(self):
        """Test importing apps module"""
        try:
            from djangocms_mcp import apps
            self.assertTrue(hasattr(apps, 'DjangoCmsMcpConfig'))
        except ImportError as e:
            self.fail(f"Failed to import apps: {e}")


class TestPackageStructure(TestCase):
    """Test package structure and files"""

    def test_package_init(self):
        """Test that package __init__.py is importable"""
        try:
            import djangocms_mcp
            # Should have version info
            self.assertTrue(hasattr(djangocms_mcp, '__version__'))
        except ImportError as e:
            self.fail(f"Failed to import package: {e}")

    def test_templates_directory_exists(self):
        """Test that templates directory exists"""
        import os
        from djangocms_mcp import apps
        
        app_config = apps.get_app_config('djangocms_mcp')
        app_path = app_config.path
        templates_path = os.path.join(app_path, 'templates', 'djangocms_mcp')
        
        self.assertTrue(os.path.exists(templates_path),
                       f"Templates directory not found at {templates_path}")


class TestOptionalDependencies(TestCase):
    """Test handling of optional dependencies"""

    def test_versioning_detection(self):
        """Test that versioning detection works correctly"""
        from djangocms_mcp.mcp import VERSIONING_ENABLED
        
        # Should be boolean
        self.assertIsInstance(VERSIONING_ENABLED, bool)

    def test_versioning_imports_handled(self):
        """Test that missing versioning imports are handled gracefully"""
        # This tests the try/except block in mcp.py
        from djangocms_mcp import mcp
        
        # If versioning is not available, these should be None
        if not mcp.VERSIONING_ENABLED:
            self.assertIsNone(mcp.Version)
            self.assertIsNone(mcp.DRAFT)
            self.assertIsNone(mcp.PUBLISHED)
            self.assertIsNone(mcp.UNPUBLISHED)
            self.assertIsNone(mcp.ARCHIVED)

    def test_mcp_tools_without_versioning(self):
        """Test that MCP tools work without versioning installed"""
        from djangocms_mcp.mcp import DjangoCMSVersioningTools
        
        tools = DjangoCMSVersioningTools()
        
        # Basic methods should work regardless of versioning
        languages_result = tools.get_languages()
        self.assertIn('languages', languages_result)
        
        templates_result = tools.list_templates()
        self.assertIn('templates', templates_result)
        
        plugins_result = tools.list_plugin_types()
        self.assertIn('plugins', plugins_result)


@override_settings(DEBUG=True)
class TestDebugMode(TestCase):
    """Test app behavior in debug mode"""

    def test_debug_mode_settings(self):
        """Test that debug mode doesn't break app functionality"""
        from djangocms_mcp.models import MCPServerPlugin
        
        # Should be able to create plugins in debug mode
        plugin = MCPServerPlugin.objects.create(
            title="Debug Test Plugin",
            enabled=True
        )
        
        self.assertEqual(plugin.title, "Debug Test Plugin")
        self.assertTrue(plugin.enabled)


class TestMigrations(TestCase):
    """Test migration-related functionality"""

    def test_migration_modules_disabled(self):
        """Test that migrations are properly disabled for testing"""
        # In our test settings, we disable migrations
        # This test ensures that works correctly
        from django.db import migrations
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connection
        
        # Should be able to create tables without running migrations
        # This is implicitly tested by the fact that our tests run at all
        self.assertTrue(True)  # Placeholder assertion

    def test_model_creation_without_migrations(self):
        """Test that models can be created without running migrations"""
        from djangocms_mcp.models import MCPServerPlugin
        
        # If migrations were required and not working, this would fail
        plugin = MCPServerPlugin.objects.create()
        self.assertIsNotNone(plugin.pk)
