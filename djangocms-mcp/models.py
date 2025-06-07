from django.db import models
from cms.models import CMSPlugin

class MCPServerPlugin(CMSPlugin):
    """Plugin to enable MCP server functionality in Django CMS"""
    title = models.CharField(max_length=200, default="MCP Server")
    description = models.TextField(blank=True, help_text="Description of MCP server functionality")
    enabled = models.BooleanField(default=True, help_text="Enable/disable MCP server")

    def __str__(self):
        return self.title