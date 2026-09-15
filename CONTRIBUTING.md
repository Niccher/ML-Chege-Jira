# Contributing to ML Chege Jira

Thank you for contributing to the ML Chege Jira service.

## Development Setup

1. Install [uv](https://github.com/astral-sh/uv):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Create virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev]"
   ```

3. Setup environment variables:
   ```bash
   cp .env.example .env
   ```

## Code Quality Standards

Before submitting any Pull Request:

1. **Linting and Formatting**:
   ```bash
   uv run ruff check app/ tests/
   uv run ruff format app/ tests/
   ```

2. **Type Checking**:
   ```bash
   uv run mypy app/
   ```

3. **Running Tests**:
   ```bash
   uv run pytest
   ```

## Commit Conventions

Follow Conventional Commits:
- `feat: add wiki generation prompt template`
- `fix: correct asyncio lock release on exception`
- `test: add unit tests for telemetry service`
- `docs: update API documentation`
