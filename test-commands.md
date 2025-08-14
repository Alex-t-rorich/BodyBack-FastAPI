# Test Commands Reference

This file contains commonly used test commands for the BodyBack FastAPI project.

## Prerequisites

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (if not already done)
pip install -r requirements.txt
```

## Basic Test Commands

### Run All Tests
```bash
# Run all unit tests
python -m pytest tests/unit/ -v

# Run all tests (when integration tests are added)
python -m pytest tests/ -v

# Quiet mode (less verbose output)
python -m pytest tests/unit/ -q
```

### Run Specific Test Categories
```bash
# Run only model tests
python -m pytest tests/unit/models/ -v

# Run only schema tests  
python -m pytest tests/unit/schemas/ -v

# Run specific test file
python -m pytest tests/unit/models/test_user.py -v

# Run specific test function
python -m pytest tests/unit/models/test_user.py::TestUserModel::test_has_role_true -v
```

### Run Tests by Markers
```bash
# Run only unit tests (when integration tests exist)
python -m pytest -m unit -v

# Run only model tests
python -m pytest -m model -v

# Run only schema tests
python -m pytest -m schema -v
```

### Pattern Matching
```bash
# Run tests matching pattern in name
python -m pytest -k "user" -v           # All tests with "user" in name
python -m pytest -k "create" -v         # All tests with "create" in name
python -m pytest -k "role and not admin" -v  # Tests with "role" but not "admin"
```

### Failure Handling
```bash
# Stop on first failure
python -m pytest tests/unit/ --maxfail=1

# Re-run only failed tests from last run
python -m pytest --lf

# Re-run failed tests first, then continue with rest
python -m pytest --ff
```

### Coverage Reports
```bash
# Run tests with coverage report
python -m pytest tests/unit/ --cov=app

# Coverage with missing lines shown
python -m pytest tests/unit/ --cov=app --cov-report=term-missing

# Generate HTML coverage report
python -m pytest tests/unit/ --cov=app --cov-report=html
# Open htmlcov/index.html in browser to view

# Coverage for specific module
python -m pytest tests/unit/ --cov=app.models --cov-report=term-missing
```

### Output Control
```bash
# Show detailed failure information
python -m pytest tests/unit/ --tb=long

# Show short failure information
python -m pytest tests/unit/ --tb=short

# Show only one line per failure
python -m pytest tests/unit/ --tb=line

# Show no traceback, just pass/fail
python -m pytest tests/unit/ --tb=no
```

### Performance and Parallel Testing
```bash
# Run tests in parallel (requires pytest-xdist)
# pip install pytest-xdist
python -m pytest tests/unit/ -n auto

# Run with timing information
python -m pytest tests/unit/ --durations=10  # Show 10 slowest tests
```

### Development Workflow Commands
```bash
# Quick feedback during development
python -m pytest tests/unit/ -x --tb=short

# Watch mode (requires pytest-watch)  
# pip install pytest-watch
ptw tests/unit/ -- --tb=short

# Test specific component during development
python -m pytest tests/unit/models/test_user.py -v --tb=short
```

### Integration Tests (Future)
```bash
# When integration tests are added:
python -m pytest tests/integration/ -v

# Run fast tests first, then slow integration tests
python -m pytest tests/unit/ && python -m pytest tests/integration/

# Skip slow tests during development
python -m pytest -m "not slow" -v
```

## Continuous Integration Commands
```bash
# Full test suite with coverage (for CI)
python -m pytest tests/ --cov=app --cov-report=xml --cov-report=term

# Strict mode - treat warnings as errors
python -m pytest tests/unit/ --strict-warnings

# Generate JUnit XML for CI systems
python -m pytest tests/unit/ --junitxml=test-results.xml
```

## Useful Aliases
Add these to your shell profile for convenience:

```bash
# Fast unit tests
alias test-unit="python -m pytest tests/unit/ -v"

# Quick test with short output
alias test-quick="python -m pytest tests/unit/ -q --tb=short"

# Test with coverage
alias test-cov="python -m pytest tests/unit/ --cov=app --cov-report=term-missing"

# Test specific patterns
alias test-models="python -m pytest tests/unit/models/ -v"
alias test-schemas="python -m pytest tests/unit/schemas/ -v"
```

## Notes
- Always run tests from the project root directory
- Activate virtual environment before running tests
- Use `-v` for verbose output during development
- Use `-q` for quiet output in CI or when running frequently
- The `--tb=short` option is great for development as it shows concise error information