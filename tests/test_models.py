"""
Test the MCPServerPlugin model and its functionality
"""
import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from djangocms_mcp.models import MCPServerPlugin


class TestMCPServerPlugin(TestCase):
    """Test the MCPServerPlugin model"""

    def test_create_plugin_with_defaults(self):
        """Test creating a plugin with default values"""
        plugin = MCPServerPlugin.objects.create()
        
        self.assertEqual(plugin.title, "MCP Server")
        self.assertEqual(plugin.description, "")
        self.assertTrue(plugin.enabled)
        self.assertEqual(str(plugin), "MCP Server")

    def test_create_plugin_with_custom_values(self):
        """Test creating a plugin with custom values"""
        plugin = MCPServerPlugin.objects.create(
            title="Custom MCP Server",
            description="A custom MCP server implementation",
            enabled=False
        )
        
        self.assertEqual(plugin.title, "Custom MCP Server")
        self.assertEqual(plugin.description, "A custom MCP server implementation")
        self.assertFalse(plugin.enabled)
        self.assertEqual(str(plugin), "Custom MCP Server")

    def test_title_max_length(self):
        """Test that title respects max_length constraint"""
        long_title = "x" * 201  # 201 characters, max is 200
        
        with self.assertRaises(ValidationError):
            plugin = MCPServerPlugin(title=long_title)
            plugin.full_clean()

    def test_title_max_length_valid(self):
        """Test that title accepts maximum valid length"""
        valid_title = "x" * 200  # Exactly 200 characters
        
        plugin = MCPServerPlugin(title=valid_title)
        plugin.full_clean()  # Should not raise
        self.assertEqual(plugin.title, valid_title)

    def test_description_can_be_blank(self):
        """Test that description can be blank"""
        plugin = MCPServerPlugin.objects.create(
            title="Test Server",
            description=""
        )
        
        self.assertEqual(plugin.description, "")

    def test_description_can_be_long(self):
        """Test that description can handle long text"""
        long_description = "This is a very long description. " * 100
        
        plugin = MCPServerPlugin.objects.create(
            title="Test Server",
            description=long_description
        )
        
        self.assertEqual(plugin.description, long_description)

    def test_enabled_default_true(self):
        """Test that enabled field defaults to True"""
        plugin = MCPServerPlugin()
        self.assertTrue(plugin.enabled)

    def test_enabled_can_be_false(self):
        """Test that enabled field can be set to False"""
        plugin = MCPServerPlugin.objects.create(
            title="Disabled Server",
            enabled=False
        )
        
        self.assertFalse(plugin.enabled)

    def test_plugin_inherits_from_cms_plugin(self):
        """Test that MCPServerPlugin properly inherits from CMSPlugin"""
        from cms.models import CMSPlugin
        
        plugin = MCPServerPlugin()
        self.assertIsInstance(plugin, CMSPlugin)

    def test_plugin_field_help_texts(self):
        """Test that help texts are properly set"""
        plugin = MCPServerPlugin()
        
        # Get field help texts from the model meta
        field_help_texts = {
            field.name: field.help_text 
            for field in plugin._meta.fields
        }
        
        self.assertEqual(
            field_help_texts.get('description'), 
            "Description of MCP server functionality"
        )
        self.assertEqual(
            field_help_texts.get('enabled'), 
            "Enable/disable MCP server"
        )

    def test_multiple_plugins_can_exist(self):
        """Test that multiple MCP server plugins can be created"""
        plugin1 = MCPServerPlugin.objects.create(
            title="Server 1",
            description="First server"
        )
        plugin2 = MCPServerPlugin.objects.create(
            title="Server 2", 
            description="Second server"
        )
        
        self.assertEqual(MCPServerPlugin.objects.count(), 2)
        self.assertNotEqual(plugin1.pk, plugin2.pk)

    def test_plugin_ordering(self):
        """Test that plugins can be ordered by title"""
        plugin_z = MCPServerPlugin.objects.create(title="Z Server")
        plugin_a = MCPServerPlugin.objects.create(title="A Server")
        plugin_m = MCPServerPlugin.objects.create(title="M Server")
        
        ordered_plugins = MCPServerPlugin.objects.order_by('title')
        titles = [p.title for p in ordered_plugins]
        
        self.assertEqual(titles, ["A Server", "M Server", "Z Server"])

    def test_update_plugin_fields(self):
        """Test updating plugin fields after creation"""
        plugin = MCPServerPlugin.objects.create(
            title="Original Title",
            description="Original description",
            enabled=True
        )
        
        # Update fields
        plugin.title = "Updated Title"
        plugin.description = "Updated description"
        plugin.enabled = False
        plugin.save()
        
        # Refresh from database
        plugin.refresh_from_db()
        
        self.assertEqual(plugin.title, "Updated Title")
        self.assertEqual(plugin.description, "Updated description")
        self.assertFalse(plugin.enabled)
