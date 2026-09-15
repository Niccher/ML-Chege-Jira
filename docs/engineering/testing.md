# Testing & Quality Assurance

This document details the test suite, test fixtures, and execution procedures for **ML Chege Jira**.

## Running Tests

Execute the automated test suite with `pytest`:

```bash
# Run all tests
pytest

# Run with verbose output and coverage report
pytest -v --cov=app --cov-report=term-missing

# Run a specific test module
pytest tests/test_health.py
```

## Test Structure & Mocking

Tests are organized inside `tests/`:
- `test_health.py`: Verifies probe responses and database connectivity flags.
- `test_security.py`: Tests API key verification, unauthorized 401 rejections, and header parsing.
- `test_tasks.py`: Mocks `LLMEngine` generation to verify prompt construction, schema validation, and database audit inserts without requiring heavy GGUF model files.
