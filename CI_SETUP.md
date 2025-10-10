# CI/CD Pipeline Setup

## Overview
A comprehensive CI/CD pipeline has been set up for the Schichtplan Sync project using GitHub Actions.

## What's Included

### 1. GitHub Actions Workflow (`.github/workflows/ci.yml`)
The workflow runs automatically on:
- Push to `master`, `main`, or `develop` branches
- Pull requests to these branches

### 2. Testing Matrix
Tests run on multiple Python versions:
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

### 3. Test Suite (`tests/`)
Comprehensive tests covering configuration, imports, and core functionality.

> 📖 **For detailed information about tests**, see [`tests/README.md`](tests/README.md)

### 4. Code Quality Checks
- **Flake8**: Catches syntax errors and undefined names
- **Pylint**: Analyzes code quality and style
- **Code Coverage**: Tracks test coverage (with Codecov integration ready)

### 5. Development Dependencies (`requirements-dev.txt`)
Additional tools for development:
- pytest and pytest-cov for testing
- flake8 and pylint for linting
- black for code formatting
- mypy for type checking

## Running Tests and Linting Locally

### Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

### Run tests:
```bash
pytest tests/ -v
```

> 📖 **For more test commands and options**, see [`tests/README.md`](tests/README.md)

### Run linting:
```bash
# Quick syntax check (catches critical errors)
flake8 . --select=E9,F63,F7,F82 --exclude=venv_schichtplan_sync

# Full linting (style and quality analysis)
pylint schichtplan_sync.py utils/*.py --max-line-length=127
```

## CI/CD Pipeline Features

### ✅ Automated Testing
Every push and pull request automatically:
1. Installs system dependencies (tesseract-ocr, poppler-utils)
2. Sets up Python environment
3. Installs all dependencies
4. Runs the full test suite
5. Reports results and coverage

### ✅ Multi-Python Support
Tests ensure compatibility across Python 3.9 through 3.12

### ✅ Fast Feedback
- Uses pip caching to speed up builds
- Runs tests in parallel across Python versions
- Provides detailed error messages on failures

### ✅ Code Quality Gates
- Blocks merges if syntax errors are found
- Provides warnings for code quality issues
- Tracks code coverage trends

## Adding Status Badges (Optional)

You can add these to your README.md to show build status:

```markdown
![CI Status](https://github.com/rh0vandir/Schichtplan_sync/workflows/CI%2FCD%20Pipeline/badge.svg)
```

## Pipeline Stages

### Stage 1: Setup
- Checkout code
- Set up Python environment (matrix: 3.9, 3.10, 3.11, 3.12)
- Install system dependencies (tesseract-ocr, poppler-utils)
- Cache pip packages for faster builds

### Stage 2: Dependencies
- Install Python packages from requirements.txt
- Install testing tools (pytest, flake8, pylint)

### Stage 3: Code Quality
- **Syntax Check**: Flake8 catches critical errors
- **Style Analysis**: Pylint analyzes code quality
- **Exit Strategy**: Syntax errors fail the build, style issues warn only

### Stage 4: Testing
- Run full test suite with pytest
- Generate coverage reports
- Upload coverage to Codecov (optional)

### Stage 5: Validation
- Test main script syntax with py_compile
- Validate all utility modules can be imported
- Check sample config is valid JSON

## What Gets Tested

See [`tests/README.md`](tests/README.md) for detailed test coverage information.

## Future Enhancements

Consider adding:
- Integration tests with test PDF files
- Performance benchmarks
- Automated deployment on successful builds
- Security scanning (Dependabot, CodeQL)
- Documentation generation

## Troubleshooting

If tests fail in CI but pass locally:
1. Check Python version compatibility
2. Verify all dependencies are in requirements.txt
3. Ensure no local environment variables are required
4. Check for file path differences (absolute vs relative)

## Workflow Configuration

### Modifying the CI Pipeline

To change the CI/CD workflow, edit `.github/workflows/ci.yml`:

**Add a Python version:**
```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12', '3.13']
```

**Add a system dependency:**
```yaml
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y tesseract-ocr poppler-utils your-package
```

**Add a testing stage:**
```yaml
- name: Your new test stage
  run: |
    your-test-command
```

## Maintaining the Pipeline

When making changes:
1. **Add new tests**: Update `tests/` directory (see `tests/README.md`)
2. **Modify workflow**: Edit `.github/workflows/ci.yml`
3. **Test locally**: Ensure tests pass before pushing
4. **Update documentation**: Keep this file and `tests/README.md` in sync

