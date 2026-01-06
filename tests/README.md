# Test Suite Documentation

## Overview

This directory contains comprehensive test suites for the Scheduler project, specifically for:
- [`test_data_generator`](../modules/test_data_generator.py:1) module
- [`template_generator`](../modules/template_generator.py:1) module  
- [`generate_templates.py`](../generate_templates.py:1) script

## Test Files

### [`test_test_data_generator.py`](test_test_data_generator.py:1)
Tests for the [`TestDataGenerator`](../modules/test_data_generator.py:16) class that generates test data for Olya, DeepSea, and Balakovo scenarios.

**Test Coverage:**
-  Initialization with default and custom directories
-  Balakovo berths generation (file creation, structure, data validity)
-  Balakovo fleet generation (vessel types, destinations)
-  Balakovo cargo plan generation (quantities, priorities, dates)
-  Balakovo parameters generation (critical params validation)
-  Balakovo restrictions generation (types, severity levels)
-  Edge cases (nonexistent directories, multiple calls, CSV format)

### [`test_template_generator.py`](test_template_generator.py:1)
Tests for the [`TemplateGenerator`](../modules/template_generator.py:16) class that creates empty CSV templates.

**Test Coverage:**
-  Initialization with default and custom directories
-  Template structure validation (columns, headers)
-  Comment headers and documentation
-  UTF-8 encoding for Russian text
-  CSV separator consistency (semicolon)
-  Template usability (Excel compatibility, example values)
-  Edge cases (overwriting, existing files)

### [`test_generate_templates_script.py`](test_generate_templates_script.py:1)
Tests for the command-line interface script [`generate_templates.py`](../generate_templates.py:1).

**Test Coverage:**
-  Script imports and structure
-  Documentation and help text
-  Generator instantiation
-  Independent execution of generators
-  Error handling scenarios

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/test_test_data_generator.py
pytest tests/test_template_generator.py
pytest tests/test_generate_templates_script.py
```

### Run with Verbose Output
```bash
pytest tests/ -v
```

### Run with Coverage Report
```bash
pytest tests/ --cov=modules --cov-report=html
```

### Run Only Fast Tests (excluding slow/integration tests)
```bash
pytest tests/ -m "not slow and not integration"
```

## Test Structure

All tests follow a consistent structure:

1. **Class-based organization**: Related tests are grouped in classes
2. **Fixtures**: Reusable test setup using pytest fixtures
3. **Clear assertions**: Descriptive assertion messages
4. **Edge cases**: Tests cover both happy paths and error scenarios

### Example Test Pattern:
```python
class TestFeatureName:
    """Test description"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)
    
    def test_specific_behavior(self, temp_dir):
        """Should do something specific"""
        # Arrange
        generator = TestDataGenerator(output_dir=temp_dir)
        
        # Act
        generator.generate_balakovo_test_data()
        
        # Assert
        assert filepath.exists(), "File should be created"
```

## Key Testing Principles

### 1. **Readability First**
- Clear test names that describe the expected behavior
- Descriptive assertion messages
- Well-organized test classes

### 2. **Comprehensive Coverage**
- Happy path scenarios
- Edge cases
- Error conditions
- Data validation

### 3. **Test Isolation**
- Each test uses temporary directories
- No shared state between tests
- Proper cleanup in fixtures

### 4. **Realistic Scenarios**
- Tests use realistic data structures
- Validation matches production requirements
- Integration scenarios included

## Common Fixtures

### `temp_dir`
Creates a temporary directory for file operations, automatically cleaned up after tests.

### `generator`
Creates a configured generator instance (TestDataGenerator or TemplateGenerator) with temp directory.

## Assertion Patterns

### File Existence
```python
assert filepath.exists(), "File should be created"
```

### DataFrame Structure
```python
assert all(col in df.columns for col in expected_columns), \
    "All required columns should be present"
```

### Data Validity
```python
assert all(df['qty_mt'] > 0), "Quantities should be positive"
```

### Set Membership
```python
assert set(df['vessel_type'].unique()).issubset({'barge', 'dry'}), \
    "Vessel types should be 'barge' or 'dry'"
```

## Continuous Integration

These tests are designed to be run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest tests/ -v --cov=modules
```

## Dependencies

Required packages (should be in `requirements.txt`):
- pytest
- pandas
- pytest-cov (for coverage reports)

## Future Enhancements

Potential areas for expanding test coverage:
- [ ] Olya test data generation methods
- [ ] DeepSea test data generation methods
- [ ] Command-line argument parsing (when implemented)
- [ ] Performance/load testing
- [ ] Data integrity across related files

## Contributing

When adding new tests:

1. Follow the existing class-based structure
2. Use descriptive test names with `test_` prefix
3. Include docstrings explaining what's being tested
4. Add clear assertion messages
5. Consider both happy path and edge cases
6. Use fixtures for common setup
7. Ensure tests are isolated and repeatable
