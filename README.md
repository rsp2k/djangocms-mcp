# Django CMS MCP Server Plugin

[![PyPI version](https://badge.fury.io/py/djangocms-mcp.svg)](https://badge.fury.io/py/djangocms-mcp)
[![Python Support](https://img.shields.io/pypi/pyversions/djangocms-mcp.svg)](https://pypi.org/project/djangocms-mcp/)
[![Django Support](https://img.shields.io/badge/django-4.0%2B-blue.svg)](https://docs.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Django CMS plugin that provides **Model Context Protocol (MCP)** server functionality, enabling AI assistants like Claude to directly interact with, manage, and create content in your Django CMS installation through natural language.

## 🚀 Features

- **Complete CMS Integration**: Full access to Django CMS pages, plugins, and templates
- **LLM-Powered Content Management**: Create, edit, and publish content through natural language
- **Multi-language Support**: Work with content in multiple languages seamlessly
- **Plugin System Integration**: Add and configure any Django CMS plugin via MCP
- **Hierarchical Page Management**: Navigate and manage complex page structures
- **Template Management**: Create pages with any available template
- **Search & Discovery**: Find content across your entire CMS
- **Publishing Workflow**: Draft, review, and publish content with proper workflow (djangocms-versioning required)
- **Security First**: Built-in authentication and permission checking

## 🎯 Use Cases

- **Content Creation**: "Create a new blog post about Django best practices"
- **Site Management**: "Update the homepage banner and publish the changes"
- **Content Organization**: "Move the pricing page under the products section"
- **Multi-language Sites**: "Translate this page to Spanish and French"
- **Plugin Management**: "Add a contact form to the about page"
- **SEO Optimization**: "Update meta descriptions for all product pages"

## 📦 Installation

### 1. Install the Package

```bash
pip install djangocms-mcp
```

### 2. Add to Django Settings

```python
# settings.py
INSTALLED_APPS = [
   # existing apps...
    'cms',
    'menus',
    'treebeard',
    'sekizai',
    'easy_thumbnails',
    # ...
    'django_cms_mcp',  # Add this line
    # ... your other apps
]

# Optional: Configure MCP settings
DJANGO_CMS_MCP = {
    'REQUIRE_AUTHENTICATION': True,
    'ALLOWED_HOSTS': ['localhost', '127.0.0.1'],
    'MAX_PLUGINS_PER_REQUEST': 50,
    'ENABLE_SEARCH': True,
    'DEBUG_MODE': False,
}
```

### 3. Include URLs

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include('mcp_server.urls')), # Be sure to include django-mcp-server urls!
    path('', include('cms.urls')),
]
```

### 4. Run Migrations

```bash
python manage.py migrate djangocms-mcp
```

## 🤖 Connecting to Claude Desktop

### Configure Claude Desktop MCP Settings

To connect Claude Desktop to your Django CMS MCP server, you need to configure the MCP settings in Claude Desktop's configuration file.

#### 1. Locate Claude Desktop Config File

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
~/.config/Claude/claude_desktop_config.json
```

#### 2. Configure the MCP Server

Add your Django CMS MCP server to the configuration file:

```json
{
  "mcpServers": {
    "django-cms": {
      "command": "python",
      "args": [
        "/path/to/your/project/manage.py",
        "start_mcp_server",
        "--host",
        "localhost",
        "--port",
        "8001"
      ],
      "env": {
        "DJANGO_SETTINGS_MODULE": "myproject.settings"
      }
    }
  }
}
```

#### 3. Alternative: HTTP-based Configuration

If you prefer to run the server separately and connect via HTTP:

```json
{
  "mcpServers": {
    "django-cms": {
      "command": "curl",
      "args": [
        "-X",
        "POST",
        "-H",
        "Content-Type: application/json",
        "http://localhost:8000/mcp/"
      ]
    }
  }
}
```

#### 4. Production Configuration Example

For production environments with authentication:

```json
{
  "mcpServers": {
    "django-cms-production": {
      "command": "python",
      "args": [
        "/var/www/mysite/manage.py",
        "start_mcp_server",
        "--host",
        "127.0.0.1",
        "--port",
        "8001"
      ],
      "env": {
        "DJANGO_SETTINGS_MODULE": "mysite.settings.production",
        "DATABASE_URL": "postgresql://user:pass@localhost/mydb",
        "SECRET_KEY": "your-secret-key-here"
      }
    }
  }
}
```

#### 5. Restart Claude Desktop

After updating the configuration file:

1. **Close Claude Desktop completely**
2. **Restart Claude Desktop**
3. **Verify the connection** by asking Claude to interact with your CMS

#### 6. Test the Connection

Once configured, you can test the connection by asking Claude:

> "Can you show me the page structure of my Django CMS site?"

Claude will use the `get_page_tree` function to retrieve and display your site's page hierarchy.

## 💻 VS Code Integration

### Installing Claude Extension for VS Code

1. **Install the Extension**:
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
   - Search for "Claude" by Anthropic
   - Click Install

2. **Configure MCP Settings in VS Code**:

Create or edit `.vscode/settings.json` in your project:

```json
{
  "claude.mcpServers": {
    "django-cms": {
      "command": "python",
      "args": [
        "${workspaceFolder}/manage.py",
        "start_mcp_server",
        "--host",
        "localhost",
        "--port",
        "8001"
      ],
      "env": {
        "DJANGO_SETTINGS_MODULE": "${workspaceFolderBasename}.settings",
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  }
}
```

3. **Workspace-Specific Configuration**:

For multi-project workspaces, create `.vscode/claude.config.json`:

```json
{
  "mcpServers": {
    "django-cms-dev": {
      "command": "${workspaceFolder}/venv/bin/python",
      "args": [
        "${workspaceFolder}/manage.py",
        "start_mcp_server"
      ],
      "env": {
        "DJANGO_SETTINGS_MODULE": "myproject.settings.development"
      },
      "cwd": "${workspaceFolder}"
    }
  }
}
```

4. **Docker Development Setup**:

If using Docker for development:

```json
{
  "claude.mcpServers": {
    "django-cms-docker": {
      "command": "docker",
      "args": [
        "exec",
        "django-cms-container",
        "python",
        "manage.py",
        "start_mcp_server",
        "--host",
        "0.0.0.0",
        "--port",
        "8001"
      ]
    }
  }
}
```

### VS Code Development Workflow

#### 1. Content Creation Workflow

Open VS Code Command Palette (Ctrl+Shift+P / Cmd+Shift+P) and use:

- **"Claude: Ask about Django CMS"** - Get information about your site structure
- **"Claude: Create CMS Content"** - Generate new pages and content
- **"Claude: Review Page Structure"** - Analyze your site organization

#### 2. Code Integration

Create a VS Code task in `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Django CMS MCP Server",
      "type": "shell",
      "command": "python",
      "args": ["manage.py", "start_mcp_server"],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      },
      "runOptions": {
        "runOn": "folderOpen"
      }
    }
  ]
}
```

#### 3. Debug Configuration

Add to `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Django CMS MCP Server",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/manage.py",
      "args": ["start_mcp_server", "--host", "localhost", "--port", "8001"],
      "django": true,
      "console": "integratedTerminal"
    }
  ]
}
```

#### 4. Integrated Terminal Commands

Use VS Code's integrated terminal for quick MCP operations:

```bash
# Start the MCP server
python manage.py start_mcp_server

# Test MCP functions directly
python manage.py shell
>>> from django_cms_mcp.mcp_server import DjangoCMSMCPServer
>>> server = DjangoCMSMCPServer()
>>> # Test functions here
```

### VS Code Snippets for Django CMS MCP

Create `.vscode/snippets/djangocms-mcp.json`:

```json
{
  "MCP Create Page": {
    "prefix": "mcp-create-page",
    "body": [
      "# Ask Claude to create a page",
      "# Example: \"Create a ${1:page-type} page titled '${2:Page Title}' using the ${3:template-name} template\""
    ],
    "description": "Template for asking Claude to create a CMS page"
  },
  "MCP Add Plugin": {
    "prefix": "mcp-add-plugin",
    "body": [
      "# Ask Claude to add content",
      "# Example: \"Add a ${1:plugin-type} plugin to the ${2:placeholder-name} placeholder on page ${3:page-id}\""
    ],
    "description": "Template for asking Claude to add a plugin"
  },
  "MCP Search Content": {
    "prefix": "mcp-search",
    "body": [
      "# Ask Claude to find content",
      "# Example: \"Find all pages containing '${1:search-term}' in ${2:language}\""
    ],
    "description": "Template for content search via Claude"
  }
}
```

### VS Code Extensions Compatibility

The Django CMS MCP server works well with these VS Code extensions:

- **Python Extension Pack** - Enhanced Python development
- **Django Extension** - Django-specific features
- **REST Client** - Test MCP HTTP endpoints
- **Thunder Client** - API testing for MCP endpoints
- **Database Client** - View CMS database content

### VS Code Project Template

Create a complete VS Code workspace template:

**djangocms-mcp.code-workspace:**
```json
{
  "folders": [
    {
      "path": "."
    }
  ],
  "settings": {
    "python.defaultInterpreterPath": "./venv/bin/python",
    "django.settingsModule": "myproject.settings",
    "claude.mcpServers": {
      "django-cms": {
        "command": "${workspaceFolder}/venv/bin/python",
        "args": ["${workspaceFolder}/manage.py", "start_mcp_server"],
        "env": {
          "DJANGO_SETTINGS_MODULE": "myproject.settings"
        }
      }
    }
  },
  "extensions": {
    "recommendations": [
      "ms-python.python",
      "batisteo.vscode-django",
      "anthropic.claude-vscode"
    ]
  }
}
```

### Troubleshooting VS Code Integration

**1. Extension Not Found**
```bash
# Install Claude extension manually
code --install-extension anthropic.claude-vscode
```

**2. Python Path Issues**
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.terminal.activateEnvironment": true
}
```

**3. Environment Variables**
```json
{
  "terminal.integrated.env.linux": {
    "DJANGO_SETTINGS_MODULE": "myproject.settings"
  },
  "terminal.integrated.env.osx": {
    "DJANGO_SETTINGS_MODULE": "myproject.settings"
  },
  "terminal.integrated.env.windows": {
    "DJANGO_SETTINGS_MODULE": "myproject.settings"
  }
}
```

### Troubleshooting Connection Issues

#### Common Issues and Solutions

**1. Server Not Starting**
```bash
# Check if the management command works
python manage.py start_mcp_server --host localhost --port 8001

# Verify Django settings
python manage.py check
```

**2. Permission Errors**
- Ensure the user running Claude Desktop has execute permissions on your Python environment
- Check that Django database permissions are properly configured

**3. Port Conflicts**
```bash
# Check if port is available
netstat -an | grep 8001

# Use a different port if needed
python manage.py start_mcp_server --port 8002
```

**4. Environment Variables**
```json
{
  "mcpServers": {
    "django-cms": {
      "command": "python",
      "args": ["/path/to/manage.py", "start_mcp_server"],
      "env": {
        "DJANGO_SETTINGS_MODULE": "myproject.settings",
        "PYTHONPATH": "/path/to/your/project",
        "PATH": "/path/to/your/venv/bin:$PATH"
      }
    }
  }
}
```

**5. Virtual Environment Issues**
If using a virtual environment, specify the full path to Python:

```json
{
  "mcpServers": {
    "django-cms": {
      "command": "/path/to/your/venv/bin/python",
      "args": [
        "/path/to/your/project/manage.py",
        "start_mcp_server"
      ]
    }
  }
}
```

### Security Considerations for Claude Desktop

When connecting Claude Desktop to your Django CMS:

1. **Use Local Connections**: Keep the MCP server on localhost when possible
2. **Limit Permissions**: Create a dedicated Django user with minimal required permissions
3. **Monitor Usage**: Enable logging to track MCP requests
4. **Firewall Rules**: Ensure the MCP port is not exposed to external networks

```python
# Example settings for Claude Desktop integration
DJANGO_CMS_MCP = {
    'REQUIRE_AUTHENTICATION': True,
    'ALLOWED_HOSTS': ['127.0.0.1', 'localhost'],
    'LOG_REQUESTS': True,
    'MAX_PLUGINS_PER_REQUEST': 25,  # Limit for safety
    'DEBUG_MODE': False,
}
```

### Method 1: Django CMS Plugin (Recommended)

1. **Add the Plugin**:
   - Go to your Django CMS admin
   - Edit any page and add the "MCP Server" plugin
   - Configure the plugin settings (title, description, enable/disable)
   - Save and publish the page

2. **Access the Server**:
   - The MCP server is automatically available at `/mcp/`
   - The plugin displays current status and available functions

### Method 2: Management Command

Start a standalone MCP server:

```bash
python manage.py start_mcp_server --host localhost --port 8001
```

### Method 3: Programmatic Access

```python
from django_cms_mcp.mcp_server import DjangoCMSMCPServer

# Initialize the server
server = DjangoCMSMCPServer()

# Use the server programmatically
response = server.get_server().handle_request({
    "method": "get_page_tree",
    "params": {"language": "en"}
})
```

## 🔧 MCP Functions Reference

### 📄 Page Management

| Function | Description | Parameters |
|----------|-------------|------------|
| `get_page_tree` | Get hierarchical page structure | `language` (optional) |
| `get_page` | Retrieve full page content with plugins | `page_id`, `language` (optional) |
| `create_page` | Create a new page | `title`, `template`, `language`, `slug`, `parent_id`, `meta_description` |
| `publish_page` | Publish a page to make it live | `page_id`, `language` |
| `search_pages` | Search pages by title or content | `query`, `language`, `published_only` |

### 🔌 Plugin Management

| Function | Description | Parameters |
|----------|-------------|------------|
| `list_plugin_types` | Get available plugin types | None |
| `create_plugin` | Add a plugin to a placeholder | `page_id`, `placeholder_slot`, `plugin_type`, `data`, `language`, `position` |
| `update_plugin` | Update existing plugin content | `plugin_id`, `data` |

### 🎨 Template & Structure

| Function | Description | Parameters |
|----------|-------------|------------|
| `list_templates` | Get available CMS templates | None |
| `get_languages` | Get configured languages | None |

## 💡 Example Usage with Claude

### Creating Content

**You**: "Create a new blog post about Python web development with Django"

**Claude**: I'll create a new blog post for you about Python web development with Django.

```python
# Claude uses these MCP calls:
create_page(
    title="Python Web Development with Django",
    template="blog_post.html",
    language="en",
    slug="python-web-development-django",
    meta_description="Complete guide to building web applications with Django framework"
)

create_plugin(
    page_id=123,
    placeholder_slot="content",
    plugin_type="TextPlugin",
    data={
        "body": "Django is a high-level Python web framework..."
    }
)
```

### Managing Site Structure

**You**: "Move the pricing page under the products section and update its title"

**Claude**: I'll reorganize your site structure and update the page title.

```python
# Claude finds the pages and restructures
search_pages(query="pricing")
search_pages(query="products")
# Then moves and updates the page
```

### Multi-language Content

**You**: "Translate the homepage to Spanish"

**Claude**: I'll create a Spanish translation of your homepage.

```python
get_page(page_id=1, language="en")  # Get English content
create_translation(page_id=1, target_language="es")  # Create Spanish version
```

## 🛡️ Security

The plugin implements multiple security layers:

- **Authentication Required**: All MCP endpoints require Django user authentication
- **Permission Checking**: Respects Django CMS page permissions
- **CSRF Protection**: Automatic CSRF token handling
- **Input Validation**: All inputs are validated and sanitized
- **Rate Limiting**: Configurable request limits (optional)

### Production Security Checklist

- [ ] Use HTTPS in production
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Set up proper authentication (OAuth, SAML, etc.)
- [ ] Enable logging and monitoring
- [ ] Regular security updates

## ⚙️ Configuration

### Available Settings

```python
# settings.py
DJANGO_CMS_MCP = {
    # Security
    'REQUIRE_AUTHENTICATION': True,
    'ALLOWED_HOSTS': ['localhost', '127.0.0.1'],
    'ALLOWED_ORIGINS': ['https://claude.ai'],
    
    # Performance
    'MAX_PLUGINS_PER_REQUEST': 50,
    'CACHE_TIMEOUT': 300,
    'ENABLE_COMPRESSION': True,
    
    # Features
    'ENABLE_SEARCH': True,
    'ENABLE_MEDIA_UPLOAD': True,
    'ENABLE_BULK_OPERATIONS': False,
    
    # Development
    'DEBUG_MODE': False,
    'LOG_REQUESTS': True,
    'VERBOSE_ERRORS': False,
}
```

### Logging Configuration

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mcp_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'mcp_server.log',
        },
    },
    'loggers': {
        'django_cms_mcp': {
            'handlers': ['mcp_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 🧪 Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/rsp2k/djangocms-mcp.git
cd djangocms-mcp

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run tests with coverage
pytest --cov=django_cms_mcp --cov-report=html
```

### Code Quality Tools

```bash
# Format code
black .
isort .

# Lint code
ruff check .
flake8

# Type checking
mypy django_cms_mcp

# Security check
bandit -r django_cms_mcp
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests

# Run with different Django/Python versions
tox
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Ensure all tests pass: `pytest`
5. Format your code: `black . && isort .`
6. Submit a pull request

### Reporting Issues

- Use the [GitHub issue tracker](https://github.com/rsp2k/djangocms-mcp/issues)
- Include Django/Python versions
- Provide minimal reproduction steps
- Include relevant logs

## 📚 Documentation

- **[API Reference](https://djangocms-mcp.readthedocs.io/api/)**
- **[Configuration Guide](https://djangocms-mcp.readthedocs.io/configuration/)**
- **[Examples](https://djangocms-mcp.readthedocs.io/examples/)**
- **[Troubleshooting](https://djangocms-mcp.readthedocs.io/troubleshooting/)**

## 🗺️ Roadmap

### Version 1.0 (Current) ✅
- [x] Support djangocms-versioning
- [x] Complete Django CMS page management
- [x] Plugin system integration with create/update/list operations
- [x] Multi-language support for all operations
- [x] Hierarchical page tree navigation
- [x] Template management and listing
- [x] Basic search functionality across pages
- [x] Publishing workflow (draft/live)
- [x] Authentication and permission checking
- [x] Django CMS plugin for easy integration
- [x] Management command for standalone server
- [x] HTTP endpoint for web-based MCP clients
- [x] Media/Filer integration support
- [x] Page extension field access
- [x] Content serialization and data handling

This project provides a complete, production-ready MCP server implementation for Django CMS. All core functionality needed for LLM-powered content management is included in the current version.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Django CMS Team** - For the amazing CMS framework
- **Anthropic** - For the Model Context Protocol specification
- **Django Community** - For the robust web framework
- **Contributors** - Thank you to all contributors who help improve this project

## 📞 Support

- **Documentation**: [https://djangocms-mcp.readthedocs.io/](https://djangocms-mcp.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/rsp2k/djangocms-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/rsp2k/djangocms-mcp/discussions)
- **Email**: [django-mcp@supported.systems](mailto:django-mcp@supported.systems)

---

**Made with ❤️ for the Django CMS and LLLMcommunity**
