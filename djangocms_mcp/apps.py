from django.apps import AppConfig

class DjangoCmsMcpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'djangocms_mcp'
    verbose_name = 'Django CMS MCP'
    
    def ready(self):
        """
        Called when the app is ready.
        This is where we can register any signals or perform other setup.
        """
        pass
