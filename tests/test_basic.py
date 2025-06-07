"""
Basic tests for djangocms_mcp package
"""
import pytest
from django.test import TestCase
from django.apps import apps
from django.conf import settings


class TestDjangoCMSMCPApp(TestCase):
    """Test the Django app configuration"""
    
    def test_app_installed(self):
        """Test that the app is properly installed"""
        self.assertIn('djangocms_mcp', settings.INSTALLED_APPS)
    
    def test_app_config(self):
        """Test that the app config is properly loaded"""
        app_config = apps.get_app_config('djangocms_mcp')
        self.assertEqual(app_config.name, 'djangocms_mcp')
        self.assertEqual(app_config.verbose_name, 'Django CMS MCP')


class TestImports(TestCase):
    """Test that all modules can be imported"""
    
    def test_import_app(self):
        """Test importing the main app module"""
        import djangocms_mcp
        self.assertTrue(hasattr(djangocms_mcp, '__version__'))
    
    def test_import_models(self):
        """Test importing models"""
        from djangocms_mcp import models
        # Should not raise ImportError
        self.assertTrue(hasattr(models, '__all__'))
    
    def test_import_cms_plugins(self):
        """Test importing CMS plugins"""
        from djangocms_mcp import cms_plugins
        # Should not raise ImportError
        self.assertTrue(hasattr(cms_plugins, '__all__'))
    
    def test_import_mcp(self):
        """Test importing MCP functionality"""
        from djangocms_mcp import mcp
        # Should not raise ImportError
        self.assertTrue(hasattr(mcp, '__all__'))


@pytest.mark.django_db
class TestMCPFunctionality(TestCase):
    """Test core MCP functionality"""
    
    def test_mcp_server_creation(self):
        """Test that MCP server can be instantiated"""
        from djangocms_mcp.mcp import DjangoCMSMCPServer
        
        server = DjangoCMSMCPServer()
        self.assertIsInstance(server, DjangoCMSMCPServer)
    
    def test_mcp_tools_available(self):
        """Test that MCP tools are properly defined"""
        from djangocms_mcp.mcp import DjangoCMSMCPServer
        
        server = DjangoCMSMCPServer()
        # Should have some tools defined
        self.assertTrue(hasattr(server, 'list_tools'))


class TestCMSIntegration(TestCase):
    """Test Django CMS integration"""
    
    def test_cms_plugins_registered(self):
        """Test that CMS plugins are properly registered"""
        from cms.plugin_pool import plugin_pool
        
        # Check if our plugins are in the pool
        plugins = plugin_pool.get_all_plugins()
        plugin_names = [plugin.__name__ for plugin in plugins]
        
        # Should have at least one plugin registered
        self.assertTrue(any('MCP' in name for name in plugin_names))
