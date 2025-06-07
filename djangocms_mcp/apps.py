from django.apps import AppConfig

class DjangoCmsMcpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'djangocms_mcp'
    verbose_name = 'Django CMS MCP Server'
    
    def ready(self):
        """
        Called when the app is ready.
        This is where we can register any signals or perform other setup.
        """
        pass


def get_app_config(app_label):
    """
    Get the app configuration for the given app label.
    This function is used by the integration tests.
    """
    from django.apps import apps
    return apps.get_app_config(app_label)
