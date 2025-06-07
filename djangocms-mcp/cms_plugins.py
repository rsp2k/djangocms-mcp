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
        context.update({
            'instance': instance,
            'mcp_enabled': instance.enabled,
        })
        return context

