# Continuous Integration (CI)

This document describes the automated validation pipelines configured for **ML Chege Jira**.

## Automated CI Checks

On every push and pull request to `main`:
1. **Ruff Linter & Formatter**:
   ```bash
   ruff check app tests
   ruff format --check app tests
   ```
2. **MyPy Type Checking**:
   ```bash
   mypy app
   ```
3. **Pytest Test Suite**:
   ```bash
   pytest --cov=app --cov-report=xml
   ```
4. **Documentation Integrity**:
   ```bash
   python scripts/lint-docs.py .
   ```
