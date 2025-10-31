# Development Setup Guide

This guide explains how to set up your development environment for the typing_bot project.

## Prerequisites

- Python 3.8 or higher
- Git

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/pycoddiy/typing_bot.git
cd typing_bot
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install the project with development dependencies
pip install -e ".[dev]"
```

### 4. Set up Pre-commit Hooks

```bash
# Install pre-commit hooks (one-time setup)
pre-commit install
```

## Development Workflow

### Running Tests

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Run all tests
pytest -v

# Run tests with coverage
coverage run -m pytest
coverage report
coverage html  # Creates htmlcov/ directory
```

### Code Quality Checks

```bash
# Run all pre-commit checks
pre-commit run --all-files

# Run individual tools
black .                    # Format code
isort .                    # Sort imports
flake8 .                   # Lint code
mypy tyrec.py             # Type check
bandit -r .               # Security scan
```

### Working with .sxt Files

The project uses `.sxt` files for typing demonstrations:

```bash
# Run examples
python tyrec.py examples/example_python.sxt
python tyrec.py examples/editor_example_vim.sxt

# Test script generation
python tyrec.py scripts/code_to_type_test.sxt
```

## GitHub Actions CI

The project uses GitHub Actions for continuous integration:

- **Tests**: Runs on Python 3.8-3.12 for every push
- **Code Quality**: Runs pre-commit, type checking, and security scans

### Local CI Simulation

To run the same checks that run in CI:

```bash
# Activate virtual environment
source venv/bin/activate

# Run the same checks as CI
pre-commit run --all-files
pytest -v --tb=short
coverage run -m pytest
mypy --ignore-missing-imports tyrec.py structured_capture.py struct_editor.py
bandit -r .
```

## Project Structure

```
typing_bot/
├── .github/workflows/     # GitHub Actions CI/CD
├── examples/             # Example .sxt files
├── scripts/              # Script templates
├── tests/                # Test suite (92 tests)
├── tyrec.py             # Main recording module
├── structured_capture.py # Core capture functionality
├── struct_editor.py     # Editor integration
└── pyproject.toml       # Project configuration
```

## IDE Setup

### VS Code

Recommended extensions:
- Python
- Pylance
- Pre-commit
- Coverage Gutters

Settings (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "editor.formatOnSave": true
}
```

### PyCharm

1. Set Project Interpreter to `./venv/bin/python`
2. Enable Black formatter
3. Configure flake8 as external tool
4. Enable pytest as test runner

## Troubleshooting

### Virtual Environment Issues

```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Import Errors

```bash
# Reinstall in development mode
pip install -e .
```

### Pre-commit Issues

```bash
# Update and reinstall hooks
pre-commit autoupdate
pre-commit install --install-hooks
```

### Test Failures

```bash
# Run tests with more verbose output
pytest -vvs

# Run specific test file
pytest tests/test_basic_commands.py -v

# Run with debugging
pytest --pdb
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Set up development environment
4. Make changes with tests
5. Run quality checks locally
6. Submit pull request

The CI will automatically run all tests and quality checks on your pull request.
