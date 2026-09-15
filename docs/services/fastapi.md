# FastAPI Service Guide

This document details the architecture, code organization, dependency injection patterns, and request lifecycle of the **FastAPI** application in `app/`.

## Directory Structure

```
app/
├── api/
│   ├── deps.py               # Dependency injection (DB session, API key verification)
│   └── v1/
│       ├── admin/            # Telemetry and config management
│       ├── resources/        # AI domain routers (tasks, sprints, time_reports, qa, async)
│       ├── health.py         # Infrastructure probe
│       ├── models.py         # Model catalog and switching
│       └── router.py         # Master v1 router aggregator
├── core/
│   ├── llm_engine.py         # llama-cpp-python wrapper & singleton manager
│   ├── prompt_builder.py     # Jinja2 template renderer
│   ├── security.py           # API key constant-time comparison
│   ├── task_manager.py       # Asynchronous background job queue
│   └── telemetry.py          # psutil hardware inspector
├── db/
│   ├── readers/              # Async MySQL readers for core entities
│   ├── writers/              # Async MySQL writers for ai_* tables
│   ├── schema_guard.py       # Startup migration check
│   └── session.py            # SQLAlchemy async engine & sessionmaker
├── config.py                 # Pydantic settings loader
└── main.py                   # Lifespan and app factory
```

## Dependency Injection Patterns

In `app/api/deps.py`:
- `get_db_session()`: Yields an async SQLAlchemy database session with automatic commit/rollback.
- `verify_api_key(x_api_key: str)`: Enforces `X-API-Key` security check on every protected router.

## Adding a New Endpoint (Recipe)

1. **Define Schema**: Create input and output models using Pydantic V2 in the domain module.
2. **Create Router**: Implement the endpoint under `app/api/v1/resources/`.
3. **Register in Master Router**: Include the new sub-router in `app/api/v1/router.py`.
4. **Write Test**: Add a test case in `tests/` verifying authentication, validation, and execution.
