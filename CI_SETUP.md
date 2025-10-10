# CI/CD Pipeline

This project uses GitHub Actions for continuous integration and continuous deployment.

## Quick Overview

The CI/CD pipeline automatically runs on every push and pull request to:
- Test code across multiple Python versions (3.9, 3.10, 3.11, 3.12)
- Run linting and code quality checks
- Generate test coverage reports
- Validate configuration files

## Status

Check the current build status: [GitHub Actions](https://github.com/rh0vandir/Schichtplan_sync/actions)

Add this badge to your README for at-a-glance status:
```markdown
![CI Status](https://github.com/rh0vandir/Schichtplan_sync/workflows/CI%2FCD%20Pipeline/badge.svg)
```

## Quick Start

### Running Tests Locally

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=. --cov-report=term-missing

# Run linting
flake8 . --select=E9,F63,F7,F82 --exclude=venv_schichtplan_sync
```

## Documentation

For detailed information, see the relevant documentation:

### 🔧 **CI/CD Workflow Configuration**
[`.github/workflows/README.md`](.github/workflows/README.md)
- GitHub Actions workflow details
- Pipeline stages and jobs
- How to modify workflows
- Troubleshooting CI issues
- Local testing of workflows

### 🧪 **Test Suite**
[`tests/README.md`](tests/README.md)
- Test structure and coverage
- Writing new tests
- Running specific tests
- Testing best practices

### 📦 **Development Tools**
[`requirements-dev.txt`](requirements-dev.txt)
- pytest and pytest-cov - Testing framework
- flake8 - Style and syntax checking
- pylint - Code quality analysis
- black - Code formatting
- mypy - Type checking

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Push / Pull Request                            │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  GitHub Actions (.github/workflows/ci.yml)      │
└────────────────┬────────────────────────────────┘
                 │
                 ├─────► Test Job (Matrix: 3.9-3.12)
                 │       ├─ Install dependencies
                 │       ├─ Lint (flake8)
                 │       ├─ Run tests (pytest)
                 │       ├─ Validate syntax
                 │       └─ Upload coverage
                 │
                 └─────► Code Quality Job
                         └─ Pylint analysis
```

## Key Features

✅ **Multi-Python Testing** - Ensures compatibility across Python 3.9-3.12  
✅ **Fast Feedback** - Parallel execution with cached dependencies  
✅ **Code Quality Gates** - Automated linting and style checks  
✅ **Coverage Tracking** - Test coverage reports on every run  
✅ **Non-Blocking Warnings** - Style issues warn but don't fail builds  

## Troubleshooting

**Tests fail in CI but pass locally?**
1. Check Python version (CI tests 3.9-3.12)
2. Verify all dependencies are in `requirements.txt`
3. Ensure no local-only configuration/environment variables

**Need more help?**
- See [`.github/workflows/README.md`](.github/workflows/README.md#troubleshooting) for detailed troubleshooting
- Check the [Actions tab](https://github.com/rh0vandir/Schichtplan_sync/actions) for logs

## Contributing

When making changes:
1. Write or update tests ([`tests/README.md`](tests/README.md))
2. Run tests locally before pushing
3. Ensure code passes linting
4. Update documentation as needed

The CI pipeline will automatically validate your changes when you push or create a pull request.
