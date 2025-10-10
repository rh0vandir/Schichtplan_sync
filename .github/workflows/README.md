# GitHub Actions Workflows

This directory contains GitHub Actions workflow definitions for continuous integration and deployment.

## Workflows

### `ci.yml` - CI/CD Pipeline

The main CI/CD pipeline that runs on every push and pull request.

**Triggers:**
- Push to `master`, `main`, or `develop` branches
- Pull requests to these branches

**Jobs:**

#### 1. `test` - Multi-Python Testing
Tests the codebase across multiple Python versions to ensure compatibility.

**Matrix Strategy:**
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

**Steps:**
1. **Checkout code** - Uses `actions/checkout@v4`
2. **Set up Python** - Uses `actions/setup-python@v5` with matrix version
3. **Cache pip packages** - Uses `actions/cache@v4` for faster builds
   - Cache key based on `requirements.txt` hash
   - Significantly speeds up subsequent runs
4. **Install system dependencies**
   - `tesseract-ocr` - OCR functionality for PDF processing
   - `poppler-utils` - PDF rendering and manipulation
5. **Install Python dependencies**
   - Runtime deps from `requirements.txt`
   - Testing tools: pytest, pytest-cov, flake8, pylint
6. **Lint with flake8**
   - **Critical check**: Stops build on syntax errors (E9, F63, F7, F82)
   - **Style check**: Warns on style issues (exit-zero, max-line-length=127)
7. **Run tests**
   - Executes full pytest suite
   - Generates coverage reports (term-missing and xml)
8. **Test main script syntax**
   - Validates `schichtplan_sync.py` compiles without errors
9. **Test utility modules**
   - Ensures all utility modules can be imported
10. **Validate sample config**
    - Checks `config.json.sample` is valid JSON
11. **Upload coverage to Codecov** (Python 3.12 only)
    - Uploads coverage.xml for tracking
    - Non-blocking (fail_ci_if_error: false)

#### 2. `code-quality` - Code Quality Analysis
Runs static code analysis to maintain code quality standards.

**Steps:**
1. **Checkout code**
2. **Set up Python 3.12**
3. **Install pylint**
4. **Analyze code with Pylint**
   - Analyzes main script and all utility modules
   - Exit-zero mode (warnings only, doesn't fail build)
   - Max line length: 127 characters

## Pipeline Features

### ✅ Automated Testing
Every push and pull request automatically:
1. Installs all dependencies (system and Python)
2. Sets up multiple Python environments
3. Runs the full test suite
4. Validates code syntax and imports
5. Reports results and coverage

### ✅ Multi-Python Support
Tests run on 4 Python versions in parallel, ensuring broad compatibility:
- Python 3.9 (older stable)
- Python 3.10 (stable)
- Python 3.11 (current)
- Python 3.12 (latest)

### ✅ Fast Feedback
- **Pip caching**: Dependencies are cached between runs
- **Parallel execution**: All Python versions test simultaneously
- **Quick failure**: Syntax errors stop the build immediately
- **Detailed reports**: Full test output and coverage metrics

### ✅ Code Quality Gates
- **Critical errors**: Syntax errors and undefined names fail the build
- **Style warnings**: Code quality issues are reported but don't block
- **Coverage tracking**: Coverage reports uploaded to Codecov
- **Consistent standards**: Max line length and complexity enforced

## Modifying Workflows

### Add a Python Version

Edit the matrix in `ci.yml`:
```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12', '3.13']
```

### Add a System Dependency

Add to the "Install system dependencies" step:
```yaml
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y tesseract-ocr poppler-utils your-new-package
```

### Add a Testing Stage

Add a new step after the existing ones:
```yaml
- name: Your new test stage
  run: |
    your-test-command
    another-command
```

### Add a New Job

Add to the `jobs` section:
```yaml
jobs:
  test:
    # ... existing test job ...
  
  code-quality:
    # ... existing code-quality job ...
  
  your-new-job:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Your step
        run: your-command
```

### Change Trigger Branches

Edit the `on` section:
```yaml
on:
  push:
    branches: [ master, main, develop, staging ]
  pull_request:
    branches: [ master, main ]
```

### Add Workflow Dispatch (Manual Trigger)

```yaml
on:
  push:
    branches: [ master, main, develop ]
  pull_request:
    branches: [ master, main, develop ]
  workflow_dispatch:  # Enables manual trigger from GitHub UI
```

## Status Badges

Add to your README.md to display build status:

```markdown
![CI Status](https://github.com/rh0vandir/Schichtplan_sync/workflows/CI%2FCD%20Pipeline/badge.svg)
```

Or with a link to the Actions page:

```markdown
[![CI Status](https://github.com/rh0vandir/Schichtplan_sync/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/rh0vandir/Schichtplan_sync/actions)
```

## Troubleshooting

### Tests Pass Locally But Fail in CI

**Python Version Mismatch**
- Check which Python version failed in the matrix
- Test locally with that specific version: `python3.9 -m pytest tests/`

**Missing Dependencies**
- Ensure all dependencies are in `requirements.txt`
- Check if you're using system packages not listed

**Environment Variables**
- CI doesn't have your local environment
- Add secrets in GitHub Settings > Secrets if needed

**File Paths**
- Use relative paths, not absolute
- Be aware of case sensitivity (CI runs on Linux)

### Workflow Not Running

- Check the branch name matches triggers (master/main/develop)
- Verify workflow file is in `.github/workflows/`
- Check for YAML syntax errors (validate with a linter)
- Look at GitHub Actions tab for error messages

### Slow Build Times

- Ensure pip caching is working (check cache hit/miss)
- Consider reducing the Python version matrix for faster feedback
- Review if all system dependencies are necessary

### Coverage Upload Fails

- Coverage upload is non-blocking, so it won't fail the build
- Check Codecov token if you want private repo support
- Ensure coverage.xml is generated before upload

## Local Testing

To test workflow changes locally before pushing:

### Validate YAML Syntax
```bash
# Use a YAML linter
pip install yamllint
yamllint .github/workflows/ci.yml
```

### Test Pipeline Steps Locally
```bash
# Install system dependencies (if on Ubuntu/Debian)
sudo apt-get install -y tesseract-ocr poppler-utils

# Install Python dependencies
pip install -r requirements.txt
pip install pytest pytest-cov flake8 pylint

# Run linting
flake8 . --select=E9,F63,F7,F82 --exclude=venv_schichtplan_sync

# Run tests
pytest tests/ -v --cov=. --cov-report=term-missing

# Validate syntax
python -m py_compile schichtplan_sync.py

# Test imports
python -c "from utils import config_loader, pdf_processor, calendar_generator"
```

### Use Act (Run GitHub Actions Locally)
```bash
# Install act: https://github.com/nektos/act
# Then run your workflow locally:
act push
```

## Best Practices

1. **Keep workflows fast**: Cache dependencies, fail fast on errors
2. **Test locally first**: Don't rely on CI to catch basic errors
3. **Use matrix strategy**: Test multiple versions when needed
4. **Non-blocking quality checks**: Let style warnings warn, not block
5. **Clear step names**: Make it easy to identify what failed
6. **Version pin actions**: Use `@v4` not `@latest` for stability
7. **Minimal permissions**: Only request what's needed
8. **Secrets for sensitive data**: Never commit credentials

## Future Enhancements

Consider adding:
- [ ] **Integration tests** with test PDF files
- [ ] **Performance benchmarks** to track performance over time
- [ ] **Automated deployment** on successful builds
- [ ] **Security scanning** (Dependabot, CodeQL, Snyk)
- [ ] **Documentation generation** and deployment
- [ ] **Release automation** with semantic versioning
- [ ] **Notification webhooks** (Slack, Discord, email)
- [ ] **Artifact uploads** (test reports, build outputs)

## Related Documentation

- **Test documentation**: [`../../tests/README.md`](../../tests/README.md)
- **Development setup**: [`../../README.md`](../../README.md)

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)

