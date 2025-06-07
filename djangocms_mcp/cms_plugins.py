from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _
from .models import MCPServerPlugin

@plugin_pool.register_plugin
class MCPServerCMSPlugin(CMSPluginBase):
    model = MCPServerPlugin
    name = _("MCP Server")
    render_template = "djangocms_mcp/mcp_server.html"
    cache = False

    def render(self, context, instance, placeholder):
        # Ensure context is a dictionary
        if context is None:
            context = {}
        
        # Create a copy to avoid modifying the original context
        render_context = context.copy() if context else {}
        
        render_context.update({
            'instance': instance,
            'mcp_enabled': getattr(instance, 'enabled', True),  # Default to True if enabled field doesn't exist
        })
        return render_context
