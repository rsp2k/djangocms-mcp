from django.db import models
from django.core.exceptions import ValidationError
from cms.models import CMSPlugin

class MCPServerPlugin(CMSPlugin):
    """Plugin to enable MCP server functionality in Django CMS"""
    title = models.CharField(max_length=200, default="MCP Server")
    description = models.TextField(blank=True, help_text="Description of MCP server functionality")
    enabled = models.BooleanField(default=True, help_text="Enable/disable MCP server")

    def clean(self):
        """Custom validation for the model"""
        super().clean()
        if len(self.title) > 200:
            raise ValidationError({'title': 'Title cannot exceed 200 characters'})

    def save(self, *args, **kwargs):
        """Override save to ensure validation"""
        self.full_clean()  # This will call clean() and field validation
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
