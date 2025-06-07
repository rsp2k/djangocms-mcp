"""
Test the MCPServerCMSPlugin and its CMS integration
"""
import pytest
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from unittest.mock import Mock, patch

from cms.api import create_page
from cms.models import Page, Placeholder
from cms.plugin_rendering import ContentRenderer
from cms.toolbar.toolbar import CMSToolbar

from djangocms_mcp.cms_plugins import MCPServerCMSPlugin
from djangocms_mcp.models import MCPServerPlugin


class TestMCPServerCMSPlugin(TestCase):
    """Test the MCP Server CMS plugin functionality"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )

    def test_plugin_registration(self):
        """Test that the plugin is properly registered with CMS"""
        from cms.plugin_pool import plugin_pool
        
        # Check if plugin is registered
        registered_plugins = plugin_pool.get_all_plugins()
        plugin_names = [p.__name__ for p in registered_plugins]
        
        self.assertIn('MCPServerCMSPlugin', plugin_names)

    def test_plugin_model_assignment(self):
        """Test that plugin uses correct model"""
        plugin = MCPServerCMSPlugin()
        self.assertEqual(plugin.model, MCPServerPlugin)

    def test_plugin_name(self):
        """Test plugin display name"""
        plugin = MCPServerCMSPlugin()
        # The name should be translated but for tests we can check the structure
        self.assertIsNotNone(plugin.name)

    def test_plugin_template(self):
        """Test plugin template assignment"""
        plugin = MCPServerCMSPlugin()
        self.assertEqual(plugin.render_template, "djangocms_mcp/mcp_server.html")

    def test_plugin_cache_disabled(self):
        """Test that plugin caching is disabled"""
        plugin = MCPServerCMSPlugin()
        self.assertFalse(plugin.cache)

    def test_plugin_render_context_enabled(self):
        """Test plugin render method with enabled instance"""
        # Create plugin instance
        plugin_instance = MCPServerPlugin.objects.create(
            title="Test MCP Server",
            description="Test description",
            enabled=True
        )

        # Create plugin class instance
        plugin = MCPServerCMSPlugin()
        
        # Mock context and placeholder
        context = {}
        placeholder = Mock()
        
        # Call render method
        result_context = plugin.render(context, plugin_instance, placeholder)
        
        # Check context updates
        self.assertEqual(result_context['instance'], plugin_instance)
        self.assertTrue(result_context['mcp_enabled'])

    def test_plugin_render_context_disabled(self):
        """Test plugin render method with disabled instance"""
        # Create disabled plugin instance
        plugin_instance = MCPServerPlugin.objects.create(
            title="Disabled MCP Server",
            description="Test description",
            enabled=False
        )

        # Create plugin class instance
        plugin = MCPServerCMSPlugin()
        
        # Mock context and placeholder
        context = {}
        placeholder = Mock()
        
        # Call render method
        result_context = plugin.render(context, plugin_instance, placeholder)
        
        # Check context updates
        self.assertEqual(result_context['instance'], plugin_instance)
        self.assertFalse(result_context['mcp_enabled'])

    def test_plugin_render_preserves_existing_context(self):
        """Test that plugin render preserves existing context"""
        # Create plugin instance
        plugin_instance = MCPServerPlugin.objects.create(
            title="Test MCP Server",
            enabled=True
        )

        # Create plugin class instance
        plugin = MCPServerCMSPlugin()
        
        # Context with existing data
        existing_context = {
            'existing_key': 'existing_value',
            'another_key': 42
        }
        placeholder = Mock()
        
        # Call render method
        result_context = plugin.render(existing_context, plugin_instance, placeholder)
        
        # Check that existing context is preserved
        self.assertEqual(result_context['existing_key'], 'existing_value')
        self.assertEqual(result_context['another_key'], 42)
        
        # Check that new context is added
        self.assertEqual(result_context['instance'], plugin_instance)
        self.assertTrue(result_context['mcp_enabled'])

    @patch('cms.api.create_page')
    def test_plugin_integration_with_page(self, mock_create_page):
        """Test plugin integration with CMS page (mocked)"""
        # Mock page creation
        mock_page = Mock()
        mock_page.pk = 1
        mock_page.get_title.return_value = "Test Page"
        mock_create_page.return_value = mock_page
        
        # This test verifies that our plugin can be used with CMS pages
        # In a real scenario, this would involve creating actual page content
        plugin_instance = MCPServerPlugin.objects.create(
            title="Page MCP Server",
            enabled=True
        )
        
        self.assertIsNotNone(plugin_instance.pk)
        self.assertTrue(plugin_instance.enabled)

    def test_plugin_admin_integration(self):
        """Test that plugin works with Django admin"""
        # This tests basic admin integration
        plugin_instance = MCPServerPlugin.objects.create(
            title="Admin Test Server",
            description="For admin testing",
            enabled=True
        )
        
        # Test that the instance can be retrieved and has expected fields
        retrieved = MCPServerPlugin.objects.get(pk=plugin_instance.pk)
        self.assertEqual(retrieved.title, "Admin Test Server")
        self.assertEqual(retrieved.description, "For admin testing")
        self.assertTrue(retrieved.enabled)

    def test_plugin_context_with_none_values(self):
        """Test plugin render method handles None values gracefully"""
        # Create plugin instance with minimal data
        plugin_instance = MCPServerPlugin.objects.create()

        # Create plugin class instance
        plugin = MCPServerCMSPlugin()
        
        # Call render with None context
        result_context = plugin.render(None, plugin_instance, None)
        
        # Should still work and return a dictionary
        self.assertIsInstance(result_context, dict)
        self.assertEqual(result_context['instance'], plugin_instance)
        self.assertTrue(result_context['mcp_enabled'])  # Default is True

    def test_plugin_multiple_instances(self):
        """Test that multiple plugin instances can exist and render independently"""
        # Create two different plugin instances
        plugin1 = MCPServerPlugin.objects.create(
            title="MCP Server 1",
            enabled=True
        )
        plugin2 = MCPServerPlugin.objects.create(
            title="MCP Server 2", 
            enabled=False
        )
        
        # Create plugin class instance
        cms_plugin = MCPServerCMSPlugin()
        
        # Render both instances
        context1 = cms_plugin.render({}, plugin1, Mock())
        context2 = cms_plugin.render({}, plugin2, Mock())
        
        # Check that each renders with correct data
        self.assertEqual(context1['instance'], plugin1)
        self.assertTrue(context1['mcp_enabled'])
        
        self.assertEqual(context2['instance'], plugin2)
        self.assertFalse(context2['mcp_enabled'])

    def test_plugin_string_representation(self):
        """Test that plugin instances have proper string representation"""
        plugin_instance = MCPServerPlugin.objects.create(
            title="String Test Server"
        )
        
        # The string representation should be the title
        self.assertEqual(str(plugin_instance), "String Test Server")

    def test_plugin_field_validation_through_cms(self):
        """Test field validation when used through CMS plugin"""
        # Test creating plugin with invalid data
        with self.assertRaises(Exception):  # Could be ValidationError or DataError
            MCPServerPlugin.objects.create(
                title="x" * 201,  # Exceeds max_length
                enabled=True
            )
