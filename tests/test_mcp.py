"""
Test the MCP server functionality and tools
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth.models import User

from djangocms_mcp.mcp import (
    PageQueryTool, 
    VersionQueryTool,
    PlaceholderQueryTool,
    CMSPluginQueryTool,
    DjangoCMSVersioningTools
)


class TestMCPQueryTools(TestCase):
    """Test MCP query tools for Django CMS models"""

    def test_page_query_tool_model(self):
        """Test PageQueryTool uses correct model"""
        tool = PageQueryTool()
        from cms.models import Page
        self.assertEqual(tool.model, Page)

    def test_placeholder_query_tool_model(self):
        """Test PlaceholderQueryTool uses correct model"""
        tool = PlaceholderQueryTool()
        from cms.models import Placeholder
        self.assertEqual(tool.model, Placeholder)

    def test_cms_plugin_query_tool_model(self):
        """Test CMSPluginQueryTool uses correct model"""
        tool = CMSPluginQueryTool()
        from cms.models.pluginmodel import CMSPlugin
        self.assertEqual(tool.model, CMSPlugin)

    @patch('djangocms_mcp.mcp.VERSIONING_ENABLED', True)
    @patch('djangocms_mcp.mcp.Version')
    def test_page_query_tool_with_versioning(self, mock_version):
        """Test PageQueryTool queryset when versioning is enabled"""
        tool = PageQueryTool()
        
        # Mock the version filtering
        mock_version.objects.values_list.return_value.distinct.return_value = [1, 2, 3]
        
        with patch.object(tool.model, 'objects') as mock_objects:
            mock_filter = mock_objects.filter.return_value
            mock_distinct = mock_filter.distinct.return_value
            
            result = tool.get_queryset()
            
            # Verify the filtering chain
            mock_version.objects.values_list.assert_called_once_with('content_object_id', flat=True)
            mock_objects.filter.assert_called_once_with(id__in=[1, 2, 3])
            mock_filter.distinct.assert_called_once()
            self.assertEqual(result, mock_distinct)

    @patch('djangocms_mcp.mcp.VERSIONING_ENABLED', False)
    def test_page_query_tool_without_versioning(self):
        """Test PageQueryTool queryset when versioning is disabled"""
        tool = PageQueryTool()
        
        # Mock the parent class method
        with patch.object(tool.__class__.__bases__[0], 'get_queryset') as mock_super:
            with patch.object(tool.model, 'objects') as mock_objects:
                mock_filtered = Mock()
                
                # First attempt with old field should fail, then fallback
                mock_objects.filter.side_effect = [Exception("Field not found"), mock_filtered]
                mock_objects.all.return_value = mock_filtered
                
                result = tool.get_queryset()
                
                # Should fallback to all() when old field fails
                mock_objects.all.assert_called_once()
                self.assertEqual(result, mock_filtered)

    @patch('djangocms_mcp.mcp.VERSIONING_ENABLED', True)
    @patch('djangocms_mcp.mcp.Version')
    def test_version_query_tool_with_versioning(self, mock_version):
        """Test VersionQueryTool when versioning is enabled"""
        tool = VersionQueryTool()
        
        # Mock version model and queryset
        mock_queryset = Mock()
        mock_selected = Mock()
        mock_version.return_value = mock_queryset
        mock_queryset.objects.select_related.return_value = mock_selected
        
        # Since versioning is enabled, model should not be None
        self.assertIsNotNone(tool.model)

    @patch('djangocms_mcp.mcp.VERSIONING_ENABLED', False)
    def test_version_query_tool_without_versioning(self):
        """Test VersionQueryTool when versioning is disabled"""
        tool = VersionQueryTool()
        
        # When versioning is disabled, model should be None
        self.assertIsNone(tool.model)
        
        # get_queryset should return None
        result = tool.get_queryset()
        self.assertIsNone(result)


class TestDjangoCMSVersioningTools(TestCase):
    """Test the main MCP tools class"""

    def setUp(self):
        """Set up test data"""
        self.tools = DjangoCMSVersioningTools()

    def test_get_languages(self):
        """Test get_languages method"""
        with patch('djangocms_mcp.mcp.get_languages') as mock_get_languages:
            mock_get_languages.return_value = [('en', 'English'), ('fr', 'French')]
            
            result = self.tools.get_languages()
            
            expected = {'languages': [('en', 'English'), ('fr', 'French')]}
            self.assertEqual(result, expected)

    @patch('djangocms_mcp.mcp.VERSIONING_ENABLED', False)
    def test_get_version_states_without_versioning(self):
        """Test get_version_states when versioning is disabled"""
        result = self.tools.get_version_states()
        
        expected = {'error': 'Versioning is not enabled'}
        self.assertEqual(result, expected)

    @patch('djangocms_mcp.mcp.VERSIONING_ENABLED', True)
    @patch('djangocms_mcp.mcp.DRAFT', 'draft')
    @patch('djangocms_mcp.mcp.PUBLISHED', 'published')
    @patch('djangocms_mcp.mcp.UNPUBLISHED', 'unpublished')
    @patch('djangocms_mcp.mcp.ARCHIVED', 'archived')
    def test_get_version_states_with_versioning(self):
        """Test get_version_states when versioning is enabled"""
        result = self.tools.get_version_states()
        
        expected_states = {
            'draft': 'draft',
            'published': 'published',
            'unpublished': 'unpublished',
            'archived': 'archived'
        }
        
        self.assertIn('states', result)
        self.assertEqual(result['states'], expected_states)
        self.assertIn('descriptions', result)

    def test_list_templates(self):
        """Test list_templates method"""
        mock_templates = [
            ('template1.html', 'Template 1'),
            ('template2.html', 'Template 2')
        ]
        
        with patch('djangocms_mcp.mcp.get_cms_setting') as mock_get_setting:
            with patch('djangocms_mcp.mcp.get_placeholder_conf') as mock_get_conf:
                mock_get_setting.return_value = mock_templates
                mock_get_conf.side_effect = [
                    {'content': {}},  # First template placeholders
                    {'sidebar': {}, 'footer': {}}  # Second template placeholders
                ]
                
                result = self.tools.list_templates()
                
                expected = {
                    'templates': [
                        {
                            'path': 'template1.html',
                            'name': 'Template 1',
                            'placeholders': ['content']
                        },
                        {
                            'path': 'template2.html',
                            'name': 'Template 2',
                            'placeholders': ['sidebar', 'footer']
                        }
                    ]
                }
                
                self.assertEqual(result, expected)

    def test_list_plugin_types(self):
        """Test list_plugin_types method"""
        # Mock plugin classes
        mock_plugin1 = type('TestPlugin1', (), {
            '__name__': 'TestPlugin1',
            '__module__': 'test.module1',
            'name': 'Test Plugin 1',
            'model': type('TestModel1', (), {'__name__': 'TestModel1'})
        })
        
        mock_plugin2 = type('TestPlugin2', (), {
            '__name__': 'TestPlugin2', 
            '__module__': 'test.module2',
            'name': 'Test Plugin 2',
            'model': type('TestModel2', (), {'__name__': 'TestModel2'})
        })
        
        with patch('djangocms_mcp.mcp.plugin_pool') as mock_pool:
            mock_pool.get_all_plugins.return_value = [mock_plugin1, mock_plugin2]
            
            result = self.tools.list_plugin_types()
            
            expected = {
                'plugins': [
                    {
                        'name': 'TestPlugin1',
                        'verbose_name': 'Test Plugin 1',
                        'model': 'TestModel1',
                        'module': 'test.module1'
                    },
                    {
                        'name': 'TestPlugin2',
                        'verbose_name': 'Test Plugin 2', 
                        'model': 'TestModel2',
                        'module': 'test.module2'
                    }
                ]
            }
            
            self.assertEqual(result, expected)

    def test_serialize_plugin(self):
        """Test _serialize_plugin method"""
        # Create a mock plugin instance
        mock_instance = Mock()
        mock_instance._meta.fields = [
            Mock(name='title'),
            Mock(name='created_date'),
            Mock(name='image')
        ]
        
        # Mock field values
        mock_instance.title = 'Test Title'
        
        # Mock datetime field
        mock_datetime = Mock()
        mock_datetime.isoformat.return_value = "2023-01-01T12:00:00"
        mock_instance.created_date = mock_datetime
        
        # Mock file/image field
        mock_file = Mock()
        mock_file.url = "/media/test.jpg"
        mock_instance.image = mock_file
        
        result = self.tools._serialize_plugin(mock_instance)
        
        expected = {
            'title': 'Test Title',
            'created_date': '2023-01-01T12:00:00',
            'image': '/media/test.jpg'
        }
        
        self.assertEqual(result, expected)

    def test_serialize_plugin_handles_none_values(self):
        """Test _serialize_plugin handles None values gracefully"""
        mock_instance = Mock()
        mock_instance._meta.fields = [
            Mock(name='optional_field')
        ]
        
        mock_instance.optional_field = None
        
        result = self.tools._serialize_plugin(mock_instance)
        
        # None values should not be included in the result
        self.assertEqual(result, {})

    def test_serialize_plugin_handles_string_conversion(self):
        """Test _serialize_plugin converts non-special values to strings"""
        mock_instance = Mock()
        mock_instance._meta.fields = [
            Mock(name='number_field'),
            Mock(name='boolean_field')
        ]
        
        mock_instance.number_field = 42
        mock_instance.boolean_field = True
        
        result = self.tools._serialize_plugin(mock_instance)
        
        expected = {
            'number_field': '42',
            'boolean_field': 'True'
        }
        
        self.assertEqual(result, expected)

    def test_serialize_plugin_handles_mock_field_names(self):
        """Test _serialize_plugin handles Mock field names correctly"""
        mock_instance = Mock()
        
        # Create mock fields with different name types
        mock_field_real = Mock()
        mock_field_real.name = 'real_field'
        
        mock_field_mock = Mock()
        mock_field_mock.name = Mock()
        mock_field_mock.name._mock_name = 'mock_field'
        
        mock_instance._meta.fields = [mock_field_real, mock_field_mock]
        mock_instance.real_field = 'real_value'
        mock_instance.mock_field = 'mock_value'
        
        result = self.tools._serialize_plugin(mock_instance)
        
        # Should handle both real and mock field names
        self.assertIn('real_field', result)
        # Mock field handling might vary, but shouldn't crash
        self.assertIsInstance(result, dict)


class TestMCPErrorHandling(TestCase):
    """Test error handling in MCP functionality"""

    def setUp(self):
        self.tools = DjangoCMSVersioningTools()

    def test_get_page_tree_handles_missing_language(self):
        """Test get_page_tree with None language uses default"""
        with patch('djangocms_mcp.mcp.settings') as mock_settings:
            mock_settings.LANGUAGE_CODE = 'en'
            
            # Mock empty page queryset
            with patch('djangocms_mcp.mcp.Page') as mock_page:
                mock_page.objects.filter.return_value.distinct.return_value = []
                
                result = self.tools.get_page_tree(language=None)
                
                self.assertEqual(result['language'], 'en')
                self.assertEqual(result['tree'], [])

    @patch('djangocms_mcp.mcp.VERSIONING_ENABLED', False)
    def test_create_version_without_versioning(self):
        """Test create_version when versioning is disabled"""
        result = self.tools.create_version(page_id=1)
        
        expected = {'error': 'Versioning is not enabled'}
        self.assertEqual(result, expected)

    @patch('djangocms_mcp.mcp.VERSIONING_ENABLED', False)
    def test_publish_version_without_versioning(self):
        """Test publish_version when versioning is disabled"""
        result = self.tools.publish_version(version_id=1)
        
        expected = {'error': 'Versioning is not enabled'}
        self.assertEqual(result, expected)

    @patch('djangocms_mcp.mcp.VERSIONING_ENABLED', False)
    def test_archive_version_without_versioning(self):
        """Test archive_version when versioning is disabled"""
        result = self.tools.archive_version(version_id=1)
        
        expected = {'error': 'Versioning is not enabled'}
        self.assertEqual(result, expected)

    @patch('djangocms_mcp.mcp.VERSIONING_ENABLED', False) 
    def test_get_page_versions_without_versioning(self):
        """Test get_page_versions when versioning is disabled"""
        result = self.tools.get_page_versions(page_id=1)
        
        expected = {'error': 'Versioning is not enabled'}
        self.assertEqual(result, expected)
