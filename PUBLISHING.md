# PyPI Publishing Setup

This repository is configured to automatically publish to PyPI when version tags are created. Here's how to set it up and use it:

## Setup Requirements

### 1. PyPI Trusted Publishing (Recommended)

The workflow uses PyPI's trusted publishing feature, which is more secure than using API tokens:

1. Go to [PyPI](https://pypi.org) and create an account if you don't have one
2. Create the project on PyPI first (upload an initial version manually or create the project)
3. Go to your project's settings on PyPI
4. Navigate to "Publishing" → "Add a new pending publisher"
5. Fill in the details:
   - **Owner**: `rsp2k`
   - **Repository name**: `djangocms-mcp`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`

### 2. Alternative: API Token Method

If you prefer using API tokens instead:

1. Generate an API token on PyPI (Account Settings → API tokens)
2. Add it as a repository secret named `PYPI_API_TOKEN`
3. Modify the publish step in `.github/workflows/publish.yml`:

```yaml
- name: Publish to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    password: ${{ secrets.PYPI_API_TOKEN }}
    verbose: true
    print-hash: true
```

## How to Publish a New Version

1. **Update the version** in `pyproject.toml`:
   ```toml
   [project]
   version = "1.1.0"  # Update this
   ```

2. **Commit your changes**:
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 1.1.0"
   git push
   ```

3. **Create and push a version tag**:
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```

4. **The workflow will automatically**:
   - Run tests across multiple Python/Django versions
   - Perform security checks
   - Build the package
   - Verify the tag matches the package version
   - Publish to PyPI
   - Create a GitHub release

## Workflow Features

- **Multi-version testing**: Tests against Python 3.10-3.13 and Django 4.2-5.1
- **Security checks**: Runs `bandit` and `safety` to check for vulnerabilities
- **Version validation**: Ensures the git tag matches the package version
- **Build verification**: Validates the built package before publishing
- **Automatic GitHub releases**: Creates releases with installation instructions
- **Manual triggering**: Can be triggered manually via GitHub Actions UI

## Troubleshooting

### Version Mismatch Error
If you get a "Tag version does not match package version" error:
- Make sure the tag (e.g., `v1.1.0`) matches the version in `pyproject.toml` (e.g., `1.1.0`)
- The tag should have a `v` prefix, but the package version should not

### Publishing Fails
- Check that PyPI trusted publishing is configured correctly
- Ensure the package name isn't already taken by someone else
- Verify all tests are passing

### Test Failures
- The workflow will not publish if any tests fail
- Check the Actions tab for detailed error logs
- Fix issues and create a new tag to retry

## Development Workflow

For development releases or testing:

1. Use development version numbers like `1.1.0.dev0`
2. Create tags like `v1.1.0.dev0`
3. These will be published as pre-releases

For production releases:
1. Use stable version numbers like `1.1.0`
2. Create tags like `v1.1.0`
3. These will be published as stable releases
