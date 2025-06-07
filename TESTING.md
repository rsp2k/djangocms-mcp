# Development and Testing

## Running Tests

This project uses pytest for testing. Tests are automatically run on GitHub Actions for multiple Python and Django versions.

### Local Testing

1. Install the package in development mode:
```bash
pip install -e .[test]
```

2. Run the full test suite:
```bash
pytest
```

3. Run tests with coverage:
```bash
pytest --cov=djangocms_mcp --cov-report=html
```

4. Run specific test files:
```bash
pytest tests/test_basic.py
```

### Test Configuration

- Tests are configured in `pytest.ini`
- Test settings are in `tests/settings.py`
- GitHub Actions workflow is in `.github/workflows/test.yml`

### Supported Versions

The tests run against:
- Python: 3.8, 3.9, 3.10, 3.11, 3.12
- Django: 4.0, 4.1, 4.2, 5.0 (with Python version compatibility)

### Code Quality

The project uses several code quality tools:
- `ruff` for linting and formatting
- `mypy` for type checking (configured in pyproject.toml)
- `pre-commit` hooks for automated checks

To run code quality checks locally:
```bash
# Install dev dependencies
pip install -e .[dev]

# Run linting
ruff check .

# Run formatting
ruff format .

# Run type checking
mypy djangocms-mcp --ignore-missing-imports
```

### GitHub Actions

The CI/CD pipeline includes:
1. **Test Matrix**: Tests across Python 3.8-3.12 and Django 4.0-5.0
2. **Minimum Version Test**: Ensures compatibility with oldest supported versions
3. **Latest Version Test**: Tests with newest available versions
4. **Package Installation Test**: Verifies the package builds and installs correctly
5. **Code Quality Checks**: Linting, formatting, and type checking

All tests must pass before merging pull requests.
