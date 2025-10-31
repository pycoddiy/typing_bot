# Test Directory

This directory contains test files for the typing bot project. Tests can be run using pytest or individual .sxt files can be tested with the structured editor.

## Running Tests

### Using pytest (Recommended)

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests

# Run specific test files
pytest tests/test_basic_commands.py
pytest tests/test_templates.py
pytest tests/test_advanced.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run parametrized tests for all .sxt files
pytest tests/test_parametrized.py -v
```

### Using Individual .sxt Files

```bash
# Basic syntax highlighting test
python struct_editor.py tests/test_highlighting.sxt
python structured_capture.py tests/comprehensive_test.sxt --preview

# Template tests
python struct_editor.py tests/if_name_test.sxt
python struct_editor.py tests/try_except_test.sxt

# Command sequence tests
python struct_editor.py tests/test_simple.sxt
python struct_editor.py tests/command_sequence_test.sxt
```

## Test Structure

### Python Test Files (pytest)
- **`conftest.py`** - Pytest configuration, fixtures, and MockEditor class
- **`test_basic_commands.py`** - Tests for basic editor commands and text editing
- **`test_templates.py`** - Tests for template functionality and Python syntax
- **`test_advanced.py`** - Tests for debugging, error handling, and advanced features
- **`test_integration.py`** - Integration tests with existing Python modules
- **`test_parametrized.py`** - Parametrized tests that run all .sxt files automatically
- **`test_utils.py`** - Test utilities, helpers, and result analysis tools

### .sxt Test Files (Structured Format)

## Template Tests

### Core Template Tests
- **`if_name_test.sxt`** - Tests basic `{{IF_NAME_MAIN}}` template functionality
- **`if_name_indented_test.sxt`** - Tests indented if __name__ template positioning
- **`try_except_test.sxt`** - Tests `{{TRY_EXCEPT}}` template functionality and cursor positioning
- **`both_templates_test.sxt`** - Tests multiple template combinations together

### Debug Template Tests
- **`clean_debug_test.sxt`** - Tests `{{PRINT_DEBUG}}` template functionality
- **`debug_test.sxt`** - General debug functionality tests
- **`debug_cursor_test.sxt`** - Tests cursor positioning in debug scenarios

## Feature Tests

### Command Processing Tests
- **`command_sequence_test.sxt`** - Tests command sequence processing and execution
- **`comprehensive_test.sxt`** - Comprehensive feature testing across multiple areas
- **`comprehensive_newline_test.sxt`** - Tests newline handling and processing

### Editor Feature Tests
- **`test_highlighting.sxt`** - Tests syntax highlighting features (used by test_syntax_highlighting.py)
- **`test_newlines.sxt`** - Tests newline processing in editor context
- **`test_redraw.sxt`** - Tests editor redraw functionality and optimization
- **`test_simple.sxt`** - Basic functionality test for core features

### Language-Specific Tests
- **`python_syntax_test.sxt`** - Tests Python syntax highlighting and processing

### Bug Fix Tests
- **`shape_bug_test.sxt`** - Tests specific bug fixes and regression prevention

## Test Categories

### 🧪 **Unit Tests**
Test individual components and features in isolation:
- Template expansion and cursor positioning
- Command processing and validation
- Syntax highlighting accuracy

### 🔄 **Integration Tests**
Test combined functionality and feature interactions:
- Multiple templates working together
- Command sequences with templates
- Editor features with different content types

### 🐛 **Regression Tests**
Prevent bugs from returning:
- Known bug scenarios and fixes
- Edge cases and error conditions
- Performance and optimization scenarios

## Usage

### Running Individual Tests

```bash
```bash
# Basic syntax highlighting test
python struct_editor.py tests/test_highlighting.sxt
python structured_capture.py tests/comprehensive_test.sxt --preview

# Template tests
python struct_editor.py tests/if_name_test.sxt
python struct_editor.py tests/try_except_test.sxt
```

### Running Automated Tests

```bash
# Test syntax highlighting (creates test_highlighting.sxt)
python test_syntax_highlighting.py

# Test editor redraw optimization
python test_redraw_optimization.py

# Test simulation functionality
python test_simulation.py
```

### Creating New Tests

When adding new features or fixing bugs:

1. **Create test file**: `new_feature_test.sxt`
2. **Document purpose**: Add description in this README
3. **Test edge cases**: Include error conditions and boundary cases
4. **Verify regression**: Ensure fix doesn't break existing functionality

## Test File Naming Convention

- **`*_test.sxt`** - Feature or component tests
- **`test_*.sxt`** - Functionality or integration tests
- **`*_bug_test.sxt`** - Specific bug fix tests

## File Organization

```
tests/
├── README.md                    # This documentation
├── Template Tests/              # Template functionality
│   ├── if_name_test.sxt
│   ├── try_except_test.sxt
│   └── both_templates_test.sxt
├── Feature Tests/               # Core feature testing
│   ├── test_highlighting.sxt
│   ├── test_simple.sxt
│   └── comprehensive_test.sxt
└── Bug Fix Tests/               # Regression prevention
    └── shape_bug_test.sxt
```

## Related Directories

- **[../examples/](../examples/)** - User-facing examples and demos
- **[../scripts/](../scripts/)** - Utility scripts for code generation
- **Root test files** - Python test scripts (test_*.py)

## Development Workflow

1. **Write test first** - Create test file demonstrating expected behavior
2. **Implement feature** - Build functionality to make test pass
3. **Verify regression** - Run related tests to ensure no breakage
4. **Document test** - Update this README with test purpose and usage

## Pytest Configuration

### Test Markers

The project uses pytest markers to categorize tests:

- **`@pytest.mark.unit`** - Fast unit tests
- **`@pytest.mark.integration`** - Integration tests that test module interactions
- **`@pytest.mark.slow`** - Tests that take longer to run

### Test Selection Examples

```bash
# Run only fast unit tests
pytest -m unit

# Run integration tests
pytest -m integration

# Skip slow tests during development
pytest -m "not slow"

# Run specific marker combinations
pytest -m "unit and not slow"
```

### Fixtures Available

- **`parser`** - StructuredParser instance for parsing .sxt files
- **`editor`** - StructuredEditor instance (may require curses)
- **`mock_editor`** - MockEditor for testing without UI requirements
- **`temp_sxt_file`** - Temporary .sxt file for testing

### Test Utilities

The `test_utils.py` module provides:

- **`SxtTestCase`** - Parser for .sxt test file format
- **`TestResultAnalyzer`** - Analysis and assertions for test results
- **`load_all_sxt_tests()`** - Load all .sxt files for parametrized testing
- **`parametrize_sxt_tests()`** - Decorator for parametrized .sxt testing

### Adding New Tests

1. **Python tests**: Add to appropriate `test_*.py` file
2. **New .sxt files**: Will be automatically included in `test_parametrized.py`
3. **Test categories**: Use appropriate pytest markers
4. **Documentation**: Update this README with test purpose

### Continuous Integration

Tests are designed to run in CI environments:
- No curses dependency in core tests
- Proper error handling for missing files
- Clear test categorization for selective running
