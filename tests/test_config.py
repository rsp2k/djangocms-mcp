"""
Test configuration and helpers for djangocms-mcp
"""
import pytest
import os
import sys
from django.test import TestCase


# Test markers for easy categorization
pytestmark = [
    pytest.mark.django_db,  # Most tests will need database access
]


class MCPTestCase(TestCase):
    """Base test case for djangocms-mcp tests"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        super().setUpClass()
        
        # Ensure our package is importable
        import djangocms_mcp
        
    def setUp(self):
        """Set up each test"""
        super().setUp()
        
        # Clear any plugin caches
        from cms.plugin_pool import plugin_pool
        plugin_pool.set_plugin_meta()


# Test data factories and fixtures
class TestDataMixin:
    """Mixin providing common test data creation methods"""
    
    def create_mcp_plugin(self, **kwargs):
        """Create an MCPServerPlugin instance with defaults"""
        from djangocms_mcp.models import MCPServerPlugin
        
        defaults = {
            'title': 'Test MCP Server',
            'description': 'Test description',
            'enabled': True
        }
        defaults.update(kwargs)
        
        return MCPServerPlugin.objects.create(**defaults)
    
    def create_test_user(self, username='testuser', **kwargs):
        """Create a test user"""
        from django.contrib.auth.models import User
        
        defaults = {
            'email': f'{username}@example.com',
            'password': 'testpass123'
        }
        defaults.update(kwargs)
        
        return User.objects.create_user(username=username, **defaults)


# Pytest fixtures for common test objects
@pytest.fixture
def mcp_plugin():
    """Fixture providing an MCPServerPlugin instance"""
    from djangocms_mcp.models import MCPServerPlugin
    
    return MCPServerPlugin.objects.create(
        title="Test MCP Server",
        description="Test description",
        enabled=True
    )


@pytest.fixture
def disabled_mcp_plugin():
    """Fixture providing a disabled MCPServerPlugin instance"""
    from djangocms_mcp.models import MCPServerPlugin
    
    return MCPServerPlugin.objects.create(
        title="Disabled MCP Server",
        description="Test description",
        enabled=False
    )


@pytest.fixture
def test_user():
    """Fixture providing a test user"""
    from django.contrib.auth.models import User
    
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def cms_plugin_instance():
    """Fixture providing MCPServerCMSPlugin instance"""
    from djangocms_mcp.cms_plugins import MCPServerCMSPlugin
    
    return MCPServerCMSPlugin()


@pytest.fixture
def mcp_tools():
    """Fixture providing DjangoCMSVersioningTools instance"""
    from djangocms_mcp.mcp import DjangoCMSVersioningTools
    
    return DjangoCMSVersioningTools()


# Skip decorators for conditional tests
requires_versioning = pytest.mark.skipif(
    'djangocms_versioning' not in sys.modules,
    reason="djangocms-versioning not installed"
)

skip_if_no_versioning = pytest.mark.skipif(
    not os.environ.get('TEST_WITH_VERSIONING', False),
    reason="Versioning tests disabled"
)


# Test collection functions
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add markers based on test file names
        if "test_models" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
            
        if "test_cms_plugins" in str(item.fspath):
            item.add_marker(pytest.mark.cms)
            item.add_marker(pytest.mark.unit)
            
        if "test_mcp" in str(item.fspath):
            item.add_marker(pytest.mark.mcp)
            item.add_marker(pytest.mark.unit)
            
        if "test_integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
            
        # Mark slow tests
        if "slow" in item.keywords or "integration" in item.keywords:
            item.add_marker(pytest.mark.slow)


# Test configuration
class TestConfig:
    """Test configuration constants"""
    
    # Test data
    SAMPLE_TITLES = [
        "Test MCP Server",
        "Production MCP Server", 
        "Development MCP Server",
        "Staging MCP Server"
    ]
    
    SAMPLE_DESCRIPTIONS = [
        "Test description",
        "Production server for live content",
        "Development server for testing",
        "Staging server for pre-production"
    ]
    
    # Test URLs and paths
    TEST_TEMPLATE_NAME = "djangocms_mcp/mcp_server.html"
    
    # Coverage targets
    MIN_COVERAGE_PERCENT = 80
