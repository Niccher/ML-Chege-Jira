# Engineering Troubleshooting Guide

This document covers compiler, package, and environment errors encountered during development of **ML Chege Jira**.

## Common Build & Toolchain Issues

### 1. `llama-cpp-python` Compilation Fails
- **Symptom**: `error: command 'cmake' failed` or missing `libopenblas.so`.
- **Cause**: Missing C/C++ development tools or OpenBLAS headers.
- **Resolution**:
  ```bash
  # Debian / Ubuntu
  sudo apt-get install -y build-essential cmake libopenblas-dev
  ```

### 2. MyPy Strict Mode Errors
- **Symptom**: `error: Function is missing a return type annotation`.
- **Cause**: MyPy is configured with `strict = true`.
- **Resolution**: Add explicit parameter and return type hints on all functions and async handlers.

### 3. SQLAlchemy Async MySQL Authentication Error
- **Symptom**: `OperationalError: (1045, "Access denied for user 'root'@'...'")`.
- **Cause**: Local MySQL credentials differ from `.env` defaults.
- **Resolution**: Update `DB_PASSWORD` in `.env` to match your local database instance.
