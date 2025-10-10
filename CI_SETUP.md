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
Comprehensive tests covering:
- **Config Loader Tests**: Validates configuration file structure and loading
- **Import Tests**: Ensures all modules can be imported without errors
- **Basic Functionality Tests**: Tests PDF comparison and core functions
- **Dependency Tests**: Verifies all required packages are available

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

## Running Tests Locally

### Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

### Run all tests:
```bash
pytest tests/ -v
```

### Run tests with coverage:
```bash
pytest tests/ -v --cov=. --cov-report=term-missing
```

### Run linting:
```bash
# Quick syntax check
flake8 . --select=E9,F63,F7,F82 --exclude=venv_schichtplan_sync

# Full linting
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

## What Gets Tested

1. **Configuration Validation**
   - Sample config is valid JSON
   - All required fields are present
   - Config can be loaded successfully

2. **Module Imports**
   - All utility modules import without errors
   - Required dependencies are available
   - Main script can be imported

3. **Core Functionality**
   - PDF comparison and hashing works
   - Error handling for invalid URLs
   - File operations work correctly

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

## Maintaining the Test Suite

When adding new features:
1. Add corresponding tests in `tests/`
2. Run tests locally before pushing
3. Update this documentation if needed
4. Keep test coverage above 70%

