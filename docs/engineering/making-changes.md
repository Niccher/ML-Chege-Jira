# Making Changes Safely

This document outlines the workflow and Definition of Done when modifying the **ML Chege Jira** codebase.

## Touch Matrix

| If you want to… | Touch these files |
|-----------------|-------------------|
| **Add an AI enhancement endpoint** | `app/api/v1/resources/`, `app/api/v1/router.py`, `app/core/prompt_builder.py`, `tests/` |
| **Add a new GGUF model** | `app/config.py` (`MODEL_FILES`), `scripts/download_model.sh`, `docs/services/ml.md` |
| **Change prompt templates** | `app/core/prompt_builder.py` or template assets |
| **Add an async background task** | `app/core/task_manager.py`, `app/api/v1/resources/background_tasks.py` |
| **Modify database schema** | `app/db/schema_guard.py`, `app/db/writers/`, `docs/architecture/data-and-storage.md` |

## Definition of Done (Contract Changes)

Before opening a pull request for API or contract modifications:
- [ ] Code implemented with type annotations verified by `mypy`.
- [ ] Automated tests written and passing under `pytest`.
- [ ] Code formatted and linted with zero errors via `ruff check` and `ruff format`.
- [ ] OpenAPI specification updated in `docs/api/openapi.yaml`.
- [ ] Documentation updated in `docs/api/contract.md` and user guides.
- [ ] `.env.example` updated if new environment variables were introduced.
