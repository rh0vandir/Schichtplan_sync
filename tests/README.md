# Test Suite

This directory contains the automated test suite for the Schichtplan Sync project.

## Overview

The test suite ensures code quality, prevents regressions, and validates that all components work correctly. Tests run automatically via GitHub Actions on every push and pull request.

## Test Structure

### `test_config_loader.py`
Tests for configuration loading and validation:
- **`TestConfigLoader`**: Configuration file structure and parsing
  - Validates sample config is valid JSON
  - Checks all required fields are present
  - Tests config loading from file
  - Validates shift structure (start/end times, names)
- **`TestConfigHelpers`**: Helper function tests
  - `get_default_continuation_days()`
  - `get_pdf_url()`

### `test_imports.py`
Import and dependency validation:
- **`TestImports`**: Module import tests
  - Main script imports correctly
  - All utility modules import without errors
  - Critical functions exist and are callable
- **`TestDependencies`**: External package tests
  - All required packages are available
  - Key packages: requests, icalendar, pdfplumber, pytesseract

### `test_basic_functionality.py`
Core functionality tests:
- **`TestPDFComparison`**: PDF content comparison
  - Hash-based change detection works correctly
  - New content detection
  - Duplicate content handling
- **`TestUtilityFunctions`**: Basic utility tests
  - Invalid URL handling
  - Hash calculation consistency

## Running Tests

### Run all tests:
```bash
pytest tests/ -v
```

### Run a specific test file:
```bash
pytest tests/test_config_loader.py -v
```

### Run a specific test class:
```bash
pytest tests/test_config_loader.py::TestConfigLoader -v
```

### Run a specific test:
```bash
pytest tests/test_config_loader.py::TestConfigLoader::test_sample_config_is_valid_json -v
```

### Run with coverage:
```bash
pytest tests/ -v --cov=. --cov-report=term-missing
```

### Run with coverage for specific modules:
```bash
pytest tests/ -v --cov=utils --cov=schichtplan_sync --cov-report=html
```

## Test Requirements

### System Dependencies
- `tesseract-ocr` - OCR functionality
- `poppler-utils` - PDF processing

### Python Packages
See `requirements.txt` for runtime dependencies and `requirements-dev.txt` for testing tools:
- `pytest` - Test framework
- `pytest-cov` - Coverage plugin
- `pytest-mock` - Mocking support (if needed)

## Writing New Tests

### Test File Naming
- Test files must start with `test_`
- Example: `test_ftp_uploader.py`

### Test Class Naming
- Test classes should start with `Test`
- Use descriptive names: `TestFTPUploader`, `TestMailUtils`

### Test Function Naming
- Test functions must start with `test_`
- Use descriptive names: `test_upload_file_success`, `test_invalid_credentials`

### Example Test Structure
```python
#!/usr/bin/env python3
"""Tests for module_name"""

import pytest
from utils.module_name import function_to_test


class TestFeatureName:
    """Test feature description"""

    def test_normal_case(self):
        """Test normal operation"""
        result = function_to_test('input')
        assert result == 'expected'

    def test_edge_case(self):
        """Test edge case handling"""
        result = function_to_test('')
        assert result is None

    def test_error_handling(self):
        """Test error conditions"""
        with pytest.raises(ValueError):
            function_to_test(None)
```

## Current Test Coverage

As of the last run:
- **Total tests**: 13
- **Status**: All passing ✓

### Covered Areas
✅ Configuration loading and validation  
✅ Module imports and dependencies  
✅ PDF comparison and hashing  
✅ Basic error handling  

### Areas for Future Testing
- [ ] FTP upload functionality (with mocking)
- [ ] Email sending (with mocking)
- [ ] PDF extraction with test files
- [ ] Calendar generation with known data
- [ ] Shift continuation logic with test cases
- [ ] Year tracking edge cases

## Testing Best Practices

1. **Keep tests independent**: Each test should be able to run on its own
2. **Use descriptive names**: Test names should explain what's being tested
3. **Test one thing**: Each test should validate one specific behavior
4. **Use fixtures**: For setup/teardown and shared test data
5. **Mock external dependencies**: FTP, email, HTTP requests
6. **Test edge cases**: Empty inputs, None values, boundary conditions
7. **Test error conditions**: Ensure proper error handling

## Continuous Integration

Tests run automatically on:
- Push to `master`, `main`, or `develop` branches
- All pull requests

See `../CI_SETUP.md` for details about the CI/CD pipeline configuration.

## Troubleshooting

### Tests pass locally but fail in CI
1. Check Python version compatibility (CI runs on 3.9-3.12)
2. Verify all dependencies are in `requirements.txt`
3. Check for absolute vs relative path issues
4. Look for environment-specific behavior

### Import errors
1. Ensure you're running from the project root
2. Check that all `__init__.py` files exist
3. Verify the module structure matches imports

### Fixture or dependency issues
1. Clear pytest cache: `pytest --cache-clear`
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check for version conflicts

## Contributing

When adding new features:
1. Write tests first (TDD approach recommended)
2. Ensure all tests pass locally
3. Aim for >80% code coverage for new code
4. Add test documentation to this README if needed
5. Update CI_SETUP.md if CI configuration changes

