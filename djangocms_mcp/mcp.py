import logging
from typing import Dict, Any, List, Optional

from cms.models import Page, Placeholder
from cms.api import create_page
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
from cms.utils.placeholder import get_placeholder_conf
from cms.utils.conf import get_cms_setting, get_languages
from django.conf import settings

logger = logging.getLogger(__name__)

# Import djangocms-versioning models and utilities
try:
    from djangocms_versioning.models import Version
    from djangocms_versioning.constants import DRAFT, PUBLISHED, UNPUBLISHED, ARCHIVED
    from djangocms_versioning.helpers import version_list_url
    VERSIONING_ENABLED = True
except ImportError as e:
    logger.exception(f"Error importing djangocms-versioning models: {e}")
    VERSIONING_ENABLED = False
    Version = None
    DRAFT = PUBLISHED = UNPUBLISHED = ARCHIVED = None


def _get_mcp_base_classes():
    """Lazy import of MCP base classes to avoid circular imports"""
    try:
        from mcp_server import ModelQueryToolset, MCPToolset
        return ModelQueryToolset, MCPToolset
    except ImportError:
        # Create mock base classes if mcp_server is not available
        class MockModelQueryToolset:
            model = None
            def get_queryset(self):
                if hasattr(self.model, 'objects'):
                    return self.model.objects.all()
                return None
        
        class MockMCPToolset:
            pass
        
        return MockModelQueryToolset, MockMCPToolset


# Base classes for MCP tools - initialized lazily
_mcp_base_classes = None

def get_mcp_base_classes():
    """Get the MCP base classes, initializing them once"""
    global _mcp_base_classes
    if _mcp_base_classes is None:
        _mcp_base_classes = _get_mcp_base_classes()
    return _mcp_base_classes


# Create proper inheritance for testing purposes
ModelQueryToolset, MCPToolset = get_mcp_base_classes()


class PageQueryTool(ModelQueryToolset):
    """Query Django CMS pages with versioning support"""
    
    def __init__(self):
        super().__init__()
        self.model = Page

    def get_queryset(self):
        """Filter pages based on versioning status"""
        if VERSIONING_ENABLED:
            # Get pages that have versions (versioned content)
            # Use a different approach that's compatible with Django CMS 4.1+
            try:
                # Try to get pages with versions using the content relationship
                from djangocms_versioning.models import Version
                versioned_page_ids = Version.objects.values_list('content_object_id', flat=True).distinct()
                return Page.objects.filter(id__in=versioned_page_ids).distinct()
            except Exception:
                # Fallback to all pages if version filtering fails
                return Page.objects.all()
        else:
            # Fallback to standard Django CMS behavior
            # Use a more compatible approach for Django CMS 4.1+
            try:
                # Try the old field first for backward compatibility
                return Page.objects.filter(publisher_is_draft=True)
            except Exception:
                # If that fails, just return all pages
                return Page.objects.all()


class VersionQueryTool(ModelQueryToolset):
    """Query Django CMS versions when versioning is enabled"""
    
    def __init__(self):
        super().__init__()
        self.model = Version if VERSIONING_ENABLED else None

    def get_queryset(self):
        if not VERSIONING_ENABLED:
            return None
        return Version.objects.select_related('content_object')


class PlaceholderQueryTool(ModelQueryToolset):
    """Query Django CMS placeholders"""
    
    def __init__(self):
        super().__init__()
        self.model = Placeholder

    def get_queryset(self):
        return Placeholder.objects.all()


class CMSPluginQueryTool(ModelQueryToolset):
    """Query Django CMS plugins"""
    
    def __init__(self):
        super().__init__()
        self.model = CMSPlugin

    def get_queryset(self):
        return CMSPlugin.objects.all()


class DjangoCMSVersioningTools(MCPToolset):
    """Django CMS management tools with versioning support"""
    
    def __init__(self):
        super().__init__()

    def get_page_tree(self, language: Optional[str] = None, state: Optional[str] = None) -> Dict[str, Any]:
        """Get the hierarchical page structure with versioning information"""
        if not language:
            language = settings.LANGUAGE_CODE

        def build_tree(page, level=0):
            page_data = {
                'id': page.pk,
                'title': page.get_title(language=language) if hasattr(page, 'get_title') else str(page),
                'slug': page.get_slug(language=language) if hasattr(page, 'get_slug') else '',
                'template': getattr(page, 'template', ''),
                'level': level,
                'children': []
            }

            if VERSIONING_ENABLED:
                # Get versioning information
                try:
                    versions = Version.objects.filter(content_object=page)
                    if state:
                        versions = versions.filter(state=state)

                    latest_version = versions.order_by('-pk').first()
                    if latest_version:
                        page_data.update({
                            'version_id': latest_version.pk,
                            'version_state': latest_version.state,
                            'version_number': latest_version.number,
                            'is_published': latest_version.state == PUBLISHED,
                            'is_draft': latest_version.state == DRAFT,
                            'is_archived': latest_version.state == ARCHIVED,
                            'created_by': latest_version.created_by.username if latest_version.created_by else None,
                            'created': latest_version.created.isoformat(),
                            'modified': latest_version.modified.isoformat(),
                        })

                        # Add URL for published versions
                        if latest_version.state == PUBLISHED:
                            page_data['url'] = page.get_absolute_url(language=language) if hasattr(page, 'get_absolute_url') else ''
                        else:
                            page_data['url'] = None
                    else:
                        page_data.update({
                            'version_state': 'unknown',
                            'is_published': False,
                        })
                except Exception as e:
                    logger.warning(f"Error getting version info for page {page.pk}: {e}")
                    page_data.update({
                        'version_state': 'unknown',
                        'is_published': False,
                    })
            else:
                # Fallback to standard Django CMS behavior
                page_data.update({
                    'url': page.get_absolute_url(language=language) if hasattr(page, 'get_absolute_url') else '',
                    'is_published': page.is_published(language) if hasattr(page, 'is_published') else False,
                })

            # Get children
            if hasattr(page, 'get_children'):
                children = page.get_children()
                if VERSIONING_ENABLED and state:
                    # Filter children by version state
                    children = [
                        child for child in children
                        if Version.objects.filter(content_object=child, state=state).exists()
                    ]

                for child in children:
                    page_data['children'].append(build_tree(child, level + 1))

            return page_data

        # Get root pages
        if VERSIONING_ENABLED:
            # Get pages with versions
            root_pages = Page.objects.filter(
                node__depth=1,  # Root level in treebeard
            ).distinct()

            if state:
                root_pages = [
                    page for page in root_pages
                    if Version.objects.filter(content_object=page, state=state).exists()
                ]
        else:
            try:
                root_pages = Page.objects.filter(level=0, publisher_is_draft=True).published()
            except Exception:
                # If the old fields don't exist, get all root pages
                root_pages = Page.objects.filter(node__depth=1)

        return {
            'tree': [build_tree(page) for page in root_pages],
            'language': language,
            'versioning_enabled': VERSIONING_ENABLED,
            'state_filter': state,
        }

    def get_page_detail(self, page_id: int, language: Optional[str] = None, version_id: Optional[int] = None) -> Dict[str, Any]:
        """Retrieve full page content with versioning information"""
        if not language:
            language = settings.LANGUAGE_CODE

        try:
            page = Page.objects.get(pk=page_id)
            result = {
                'id': page.pk,
                'language': language
            }

            if VERSIONING_ENABLED:
                # Get specific version or latest
                if version_id:
                    try:
                        version = Version.objects.get(pk=version_id, content_object=page)
                    except Version.DoesNotExist:
                        return {'error': f'Version {version_id} not found for page {page_id}'}
                else:
                    version = Version.objects.filter(content_object=page).order_by('-pk').first()

                if not version:
                    return {'error': f'No versions found for page {page_id}'}

                # Get content from the specific version
                versioned_page = version.content_object
                result.update({
                    'version_id': version.pk,
                    'version_state': version.state,
                    'version_number': version.number,
                    'is_published': version.state == PUBLISHED,
                    'is_draft': version.state == DRAFT,
                    'is_archived': version.state == ARCHIVED,
                    'created_by': version.created_by.username if version.created_by else None,
                    'created': version.created.isoformat(),
                    'modified': version.modified.isoformat(),
                    'title': versioned_page.get_title(language=language) if hasattr(versioned_page, 'get_title') else str(versioned_page),
                    'slug': versioned_page.get_slug(language=language) if hasattr(versioned_page, 'get_slug') else '',
                    'meta_description': versioned_page.get_meta_description(language=language) if hasattr(versioned_page, 'get_meta_description') else '',
                    'template': getattr(versioned_page, 'template', ''),
                })

                # Get all versions for this page
                all_versions = Version.objects.filter(content_object=page).order_by('-created')
                result['all_versions'] = [
                    {
                        'id': v.pk,
                        'number': v.number,
                        'state': v.state,
                        'created': v.created.isoformat(),
                        'created_by': v.created_by.username if v.created_by else None,
                    }
                    for v in all_versions
                ]

            else:
                # Fallback to standard Django CMS
                result.update({
                    'title': page.get_title(language=language),
                    'slug': page.get_slug(language=language),
                    'meta_description': page.get_meta_description(language=language),
                    'template': page.template,
                    'is_published': page.is_published(language),
                    'creation_date': page.creation_date.isoformat(),
                    'changed_date': page.changed_date.isoformat(),
                })

            # Get placeholders and plugins
            placeholders_data = []
            for placeholder in page.placeholders.all():
                plugins_data = []
                plugins = placeholder.get_plugins(language=language)

                for plugin in plugins:
                    plugin_instance = plugin.get_plugin_instance()[0]
                    if plugin_instance:
                        plugins_data.append({
                            'id': plugin.pk,
                            'plugin_type': plugin.plugin_type,
                            'position': plugin.position,
                            'data': self._serialize_plugin(plugin_instance)
                        })

                placeholders_data.append({
                    'slot': placeholder.slot,
                    'plugins': plugins_data
                })

            result['placeholders'] = placeholders_data
            return result

        except Page.DoesNotExist:
            return {'error': f'Page with id {page_id} not found'}

    def create_page(
        self,
        title: str,
        template: str,
        language: Optional[str] = None,
        slug: Optional[str] = None,
        parent_id: Optional[int] = None,
        meta_description: Optional[str] = None,
        create_as_draft: bool = True
    ) -> Dict[str, Any]:
        """Create a new page with versioning support"""
        if not language:
            language = settings.LANGUAGE_CODE

        try:
            parent = None
            if parent_id:
                parent = Page.objects.get(pk=parent_id)

            page = create_page(
                title=title,
                template=template,
                language=language,
                slug=slug,
                parent=parent,
                meta_description=meta_description
            )

            result = {
                'success': True,
                'page_id': page.pk,
                'title': page.get_title(language=language),
                'slug': page.get_slug(language=language),
            }

            if VERSIONING_ENABLED:
                # Get the version that was created
                version = Version.objects.filter(content_object=page).first()
                if version:
                    result.update({
                        'version_id': version.pk,
                        'version_state': version.state,
                        'version_number': version.number,
                        'created_by': version.created_by.username if version.created_by else None,
                    })

                    # Only add URL if published
                    if version.state == PUBLISHED:
                        result['url'] = page.get_absolute_url(language=language)
            else:
                result['url'] = page.get_absolute_url(language=language)

            return result

        except Exception as e:
            logger.error(f"Error creating page: {e}")
            return {'error': str(e)}

    def publish_version(self, version_id: int, language: Optional[str] = None) -> Dict[str, Any]:
        """Publish a specific version"""
        if not VERSIONING_ENABLED:
            return {'error': 'Versioning is not enabled'}

        if not language:
            language = settings.LANGUAGE_CODE

        try:
            version = Version.objects.get(pk=version_id)

            if version.state != DRAFT:
                return {'error': f'Version {version_id} is not in draft state (current: {version.state})'}

            # Publish the version
            version.publish(language)

            # Refresh from database
            version.refresh_from_db()

            return {
                'success': True,
                'version_id': version.pk,
                'new_state': version.state,
                'page_id': version.content_object.pk,
                'published_url': version.content_object.get_absolute_url(language=language) if hasattr(version.content_object, 'get_absolute_url') else None
            }

        except Version.DoesNotExist:
            return {'error': f'Version with id {version_id} not found'}
        except Exception as e:
            logger.error(f"Error publishing version: {e}")
            return {'error': str(e)}

    def create_version(self, page_id: int, copy_from_version_id: Optional[int] = None) -> Dict[str, Any]:
        """Create a new version of a page"""
        if not VERSIONING_ENABLED:
            return {'error': 'Versioning is not enabled'}

        try:
            page = Page.objects.get(pk=page_id)

            # Get the source version
            if copy_from_version_id:
                source_version = Version.objects.get(pk=copy_from_version_id, content_object=page)
            else:
                # Use the latest published version
                source_version = Version.objects.filter(
                    content_object=page,
                    state=PUBLISHED
                ).order_by('-pk').first()

            if not source_version:
                return {'error': f'No published version found to copy from for page {page_id}'}

            # Create new version
            new_version = source_version.copy()

            return {
                'success': True,
                'version_id': new_version.pk,
                'version_state': new_version.state,
                'version_number': new_version.number,
                'page_id': page.pk,
                'copied_from_version': source_version.pk,
            }

        except (Page.DoesNotExist, Version.DoesNotExist) as e:
            return {'error': str(e)}
        except Exception as e:
            logger.error(f"Error creating version: {e}")
            return {'error': str(e)}

    def get_page_versions(self, page_id: int) -> Dict[str, Any]:
        """Get all versions of a page"""
        if not VERSIONING_ENABLED:
            return {'error': 'Versioning is not enabled'}

        try:
            page = Page.objects.get(pk=page_id)
            versions = Version.objects.filter(content_object=page).order_by('-created')

            versions_data = []
            for version in versions:
                versions_data.append({
                    'id': version.pk,
                    'number': version.number,
                    'state': version.state,
                    'created': version.created.isoformat(),
                    'modified': version.modified.isoformat(),
                    'created_by': version.created_by.username if version.created_by else None,
                    'is_current': version.state in [DRAFT, PUBLISHED],
                })

            return {
                'page_id': page_id,
                'versions': versions_data,
                'total_versions': len(versions_data),
            }

        except Page.DoesNotExist:
            return {'error': f'Page with id {page_id} not found'}

    def archive_version(self, version_id: int) -> Dict[str, Any]:
        """Archive a specific version"""
        if not VERSIONING_ENABLED:
            return {'error': 'Versioning is not enabled'}

        try:
            version = Version.objects.get(pk=version_id)

            if version.state == ARCHIVED:
                return {'error': f'Version {version_id} is already archived'}

            # Archive the version
            version.state = ARCHIVED
            version.save()

            return {
                'success': True,
                'version_id': version.pk,
                'new_state': version.state,
                'page_id': version.content_object.pk,
            }

        except Version.DoesNotExist:
            return {'error': f'Version with id {version_id} not found'}
        except Exception as e:
            logger.error(f"Error archiving version: {e}")
            return {'error': str(e)}

    def list_templates(self) -> Dict[str, Any]:
        """Get available Django CMS templates"""
        templates = get_cms_setting('TEMPLATES')
        template_list = []

        for template_path, template_name in templates:
            # Get placeholder configuration for template
            placeholder_conf = get_placeholder_conf('template', template_path, {})
            placeholders = list(placeholder_conf.keys()) if placeholder_conf else []

            template_list.append({
                'path': template_path,
                'name': template_name,
                'placeholders': placeholders
            })

        return {'templates': template_list}

    def list_plugin_types(self) -> Dict[str, Any]:
        """Get available plugin types in Django CMS"""
        plugins = []

        for plugin_class in plugin_pool.get_all_plugins():
            plugins.append({
                'name': plugin_class.__name__,
                'verbose_name': str(plugin_class.name),
                'model': plugin_class.model.__name__,
                'module': plugin_class.__module__
            })

        return {'plugins': plugins}

    def search_pages(
        self,
        query: str,
        language: Optional[str] = None,
        state: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search pages by title with versioning support"""
        if not language:
            language = settings.LANGUAGE_CODE

        if VERSIONING_ENABLED:
            # Search in versioned content
            try:
                # Get pages with versions using a compatible approach
                from djangocms_versioning.models import Version
                versioned_page_ids = Version.objects.values_list('content_object_id', flat=True).distinct()
                pages = Page.objects.filter(id__in=versioned_page_ids).distinct()
            except Exception:
                # Fallback if version filtering fails
                pages = Page.objects.all()

            if state:
                try:
                    # Filter by version state
                    versioned_page_ids_with_state = Version.objects.filter(state=state).values_list('content_object_id', flat=True).distinct()
                    pages = pages.filter(id__in=versioned_page_ids_with_state)
                except Exception:
                    pass

            # Search in titles
            title_matches = pages.filter(
                title_set__title__icontains=query,
                title_set__language=language
            ).distinct()

            results = []
            for page in title_matches:
                # Get the version info
                try:
                    version_qs = Version.objects.filter(content_object=page)
                    if state:
                        version_qs = version_qs.filter(state=state)

                    latest_version = version_qs.order_by('-pk').first()
                    if latest_version:
                        results.append({
                            'id': page.pk,
                            'title': page.get_title(language=language),
                            'slug': page.get_slug(language=language),
                            'url': page.get_absolute_url(language=language) if latest_version.state == PUBLISHED else None,
                            'version_id': latest_version.pk,
                            'version_state': latest_version.state,
                            'is_published': latest_version.state == PUBLISHED,
                        })
                except Exception:
                    # Skip pages that have version issues
                    continue
        else:
            # Fallback to standard Django CMS
            try:
                pages = Page.objects.filter(publisher_is_draft=True)
            except Exception:
                # If old field doesn't exist, use all pages
                pages = Page.objects.all()
            
            title_matches = pages.filter(
                title_set__title__icontains=query,
                title_set__language=language
            ).distinct()

            results = []
            for page in title_matches:
                results.append({
                    'id': page.pk,
                    'title': page.get_title(language=language),
                    'slug': page.get_slug(language=language),
                    'url': page.get_absolute_url(language=language),
                    'is_published': page.is_published(language)
                })

        return {
            'results': results,
            'count': len(results),
            'query': query,
            'versioning_enabled': VERSIONING_ENABLED,
            'state_filter': state,
        }

    def get_languages(self) -> Dict[str, Any]:
        """Get configured languages for the CMS"""
        return dict(
            languages=get_languages()
        )

    def get_version_states(self) -> Dict[str, Any]:
        """Get available version states when versioning is enabled"""
        if not VERSIONING_ENABLED:
            return {'error': 'Versioning is not enabled'}

        return {
            'states': {
                'draft': DRAFT,
                'published': PUBLISHED,
                'unpublished': UNPUBLISHED,
                'archived': ARCHIVED,
            },
            'descriptions': {
                DRAFT: 'Draft - work in progress, not visible to public',
                PUBLISHED: 'Published - live and visible to public',
                UNPUBLISHED: 'Unpublished - taken offline but not archived',
                ARCHIVED: 'Archived - historical version, not editable',
            }
        }

    def _serialize_plugin(self, plugin_instance):
        """Serialize plugin instance data"""
        data = {}
        if plugin_instance and hasattr(plugin_instance, '_meta'):
            for field in plugin_instance._meta.fields:
                # Handle both real field objects and Mock objects
                if hasattr(field, 'name'):
                    # For real Django fields, field.name is always a string
                    # For Mock objects in tests, we need to handle them carefully
                    field_name = field.name
                    if hasattr(field_name, '_mock_name'):
                        # This is a Mock object - extract the actual name
                        field_name = getattr(field, 'name', 'unknown_field')
                    else:
                        # Real field name - convert to string just to be safe
                        field_name = str(field_name)
                    
                    # Ensure field_name is actually a string before using getattr
                    if isinstance(field_name, str):
                        value = getattr(plugin_instance, field_name, None)
                        if value is not None:
                            if hasattr(value, 'isoformat'):  # datetime
                                data[field_name] = value.isoformat()
                            elif hasattr(value, 'url'):  # file/image fields
                                data[field_name] = value.url
                            else:
                                data[field_name] = str(value)
        return data
